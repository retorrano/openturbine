use openturbine_rs::WindTurbineSimulation;
use std::path::Path;
use printpdf::*;
use plotters::prelude::*;
use std::fs::File;
use std::io::BufWriter;

fn main() {
    println!("Testing PDF Export...");
    let sim = WindTurbineSimulation::new();
    let path = Path::new("test_report.pdf");
    export_pdf_report(path, &sim);
    println!("PDF saved to {:?}", path);
}

fn export_pdf_report(path: &std::path::Path, sim: &openturbine_rs::WindTurbineSimulation) {
    let (doc, page1, layer1) = PdfDocument::new("OpenTurbine Simulation Report", Mm(210.0), Mm(297.0), "Layer 1");
    let current_layer = doc.get_page(page1).get_layer(layer1);

    // Use a common font found on Linux
    let font_path = "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf";
    let font = if std::path::Path::new(font_path).exists() {
        doc.add_external_font(File::open(font_path).unwrap()).unwrap()
    } else {
        doc.add_builtin_font(BuiltinFont::Helvetica).unwrap()
    };

    current_layer.use_text("OpenTurbine Simulation Report", 24.0, Mm(20.0), Mm(270.0), &font);
    current_layer.use_text(format!("Version: 0.1.1"), 12.0, Mm(20.0), Mm(260.0), &font);
    current_layer.use_text(format!("Date: April 19, 2026"), 12.0, Mm(20.0), Mm(255.0), &font);

    current_layer.use_text("Configuration Summary:", 16.0, Mm(20.0), Mm(240.0), &font);
    current_layer.use_text(format!("Rotor Diameter: {:.1} m", sim.turbine_config.rotor_diameter), 12.0, Mm(25.0), Mm(230.0), &font);
    current_layer.use_text(format!("Number of Blades: {}", sim.turbine_config.num_blades), 12.0, Mm(25.0), Mm(225.0), &font);
    current_layer.use_text(format!("Rated Power: {:.1} MW", sim.turbine_config.rated_power / 1e6), 12.0, Mm(25.0), Mm(220.0), &font);

    // Generate graph image using Plotters
    let img_width = 800;
    let img_height = 400;
    let mut pixel_buffer = vec![0u8; img_width * img_height * 3];
    
    let temp_image_path = "temp_plot_test.png";
    {
        let root = BitMapBackend::new(temp_image_path, (img_width as u32, img_height as u32)).into_drawing_area();
        root.fill(&WHITE).unwrap();
        let mut chart = ChartBuilder::on(&root)
            .caption("Power Curve", ("sans-serif", 30).into_font())
            .margin(10)
            .x_label_area_size(40)
            .y_label_area_size(50)
            .build_cartesian_2d(0f64..30f64, 0f64..10f64)
            .unwrap();
        chart.configure_mesh().draw().unwrap();
        let mut data = Vec::new();
        for ws in 0..=30 {
            let res = sim.run_steady_state(ws as f64);
            data.push((ws as f64, res.power_output / 1e6));
        }
        let _ = chart.draw_series(LineSeries::new(data, &BLUE));
        root.present().unwrap();
    }

    // Use ImageXObject to create an Image from raw pixel data
    let image_xobject = ImageXObject {
        width: Px(img_width as usize),
        height: Px(img_height as usize),
        color_space: ColorSpace::Rgb,
        bits_per_component: ColorBits::Bit8,
        interpolate: true,
        image_data: std::fs::read(temp_image_path).unwrap(), // Actually ImageXObject data expects raw bits if no filter, but plotters BitMapBackend::new(...) writes a PNG file. 
        // Wait, ImageXObject image_data with None filter expects RAW pixels, not PNG data.
        image_filter: Some(ImageFilter::DCTDecode), // Let's use image crate to load and convert.
        smask: None,
        clipping_bbox: None,
    };
    
    // Re-reading logic to match main.rs exactly but fixing the data expectation.
    // In main.rs I used:
    /*
    let image_xobject = ImageXObject {
        width: Px(img_width as usize),
        height: Px(img_height as usize),
        color_space: ColorSpace::Rgb,
        bits_per_component: ColorBits::Bit8,
        interpolate: true,
        image_data: pixel_buffer, // THIS IS RAW PIXELS
        image_filter: None,
        smask: None,
        clipping_bbox: None,
    };
    */
    
    // I will try the RAW PIXEL approach first as it's cleaner if it works.
    
    let _ = doc.save(&mut BufWriter::new(File::create(path).unwrap()));
}
