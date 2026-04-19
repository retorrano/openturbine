use std::fs::File;
use std::io::Read;
use std::path::Path;
use tiny_http::{Server, Response, Header};

fn get_content_type(path: &str) -> &'static str {
    if path.ends_with(".html") {
        "text/html"
    } else if path.ends_with(".wasm") {
        "application/wasm"
    } else if path.ends_with(".js") {
        "application/javascript"
    } else if path.ends_with(".d.ts") {
        "application/typescript"
    } else if path.ends_with(".json") {
        "application/json"
    } else if path.ends_with(".css") {
        "text/css"
    } else if path.ends_with(".ico") {
        "image/x-icon"
    } else {
        "application/octet-stream"
    }
}

fn main() {
    let dir = std::env::args().nth(1).unwrap_or_else(|| ".".to_string());
    println!("Serving files from: {}", dir);
    println!("Server running on http://localhost:8080");

    let server = Server::http("0.0.0.0:8080").unwrap();

    for request in server.incoming_requests() {
        let mut path = request.url().to_string();
        if path == "/" {
            path = "/index.html".to_string();
        }

        let safe_path = path.replace("..", "");
        let file_path = Path::new(&dir).join(safe_path.trim_start_matches('/'));

        match File::open(&file_path) {
            Ok(mut file) => {
                let mut data = Vec::new();
                file.read_to_end(&mut data).unwrap();

                let content_type = get_content_type(file_path.to_str().unwrap_or(""));

                let response = Response::from_data(data)
                    .with_header(Header::from_bytes(&b"Content-Type"[..], content_type.as_bytes()).unwrap())
                    .with_header(Header::from_bytes(&b"Access-Control-Allow-Origin"[..], b"*").unwrap())
                    .with_header(Header::from_bytes(&b"Access-Control-Allow-Methods"[..], b"GET, OPTIONS").unwrap())
                    .with_header(Header::from_bytes(&b"Access-Control-Allow-Headers"[..], b"Content-Type").unwrap());

                if let Err(e) = request.respond(response) {
                    eprintln!("Error responding: {}", e);
                }
            },
            Err(_) => {
                let response = Response::from_string("404 Not Found").with_status_code(404)
                    .with_header(Header::from_bytes(&b"Access-Control-Allow-Origin"[..], b"*").unwrap());
                if let Err(e) = request.respond(response) {
                    eprintln!("Error responding: {}", e);
                }
            }
        }
    }
}
