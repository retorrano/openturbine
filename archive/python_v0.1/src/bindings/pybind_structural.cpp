#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(openturbine_struct, m) {
    m.doc() = "OpenTurbine structural module bindings";
}
