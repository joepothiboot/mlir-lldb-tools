cmake_minimum_required(VERSION 3.20)
project(toy-schema LANGUAGES CXX C)
find_package(MLIR REQUIRED CONFIG)
include(TableGen)
include(AddLLVM)
include(AddMLIR)
include_directories(${LLVM_INCLUDE_DIRS} ${MLIR_INCLUDE_DIRS} ${PROJECT_SOURCE_DIR}/include ${PROJECT_BINARY_DIR}/include)

set(LLVM_TARGET_DEFINITIONS include/ToySchema/ToySchemaOps.td)
mlir_tablegen(ToySchema/ToySchemaOps.h.inc -gen-op-decls)
mlir_tablegen(ToySchema/ToySchemaOps.cpp.inc -gen-op-defs)
mlir_tablegen(ToySchema/ToySchemaDialect.h.inc -gen-dialect-decls -dialect=toy_schema)
mlir_tablegen(ToySchema/ToySchemaDialect.cpp.inc -gen-dialect-defs -dialect=toy_schema)
add_public_tablegen_target(ToySchemaOpsIncGen)

add_mlir_dialect_library(MLIRToySchema
  lib/ToySchema/ToySchemaDialect.cpp
  lib/ToySchema/ToySchemaOps.cpp
  lib/ToySchema/FoldConstraints.cpp
  lib/ToySchema/LowerToLLVM.cpp
  DEPENDS ToySchemaOpsIncGen)

add_executable(schemac-opt tools/schemac-opt/schemac-opt.cpp)
target_link_libraries(schemac-opt PRIVATE MLIRToySchema MLIROptLib)