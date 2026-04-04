#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(openturbine_control, m) {
    m.doc() = "OpenTurbine control module bindings";
}
