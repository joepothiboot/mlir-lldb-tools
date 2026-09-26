#include "ToySchema/ToySchemaDialect.h"
#include "ToySchema/ToySchemaOps.h"
using namespace mlir;
using namespace toy_schema;
#include "ToySchema/ToySchemaDialect.cpp.inc"
void ToySchemaDialect::initialize() {
  addOperations<#define GET_OP_LIST\n#include "ToySchema/ToySchemaOps.cpp.inc">();
}
