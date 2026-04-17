#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(openturbine_env, m) {
    m.doc() = "OpenTurbine environmental module bindings";
}
