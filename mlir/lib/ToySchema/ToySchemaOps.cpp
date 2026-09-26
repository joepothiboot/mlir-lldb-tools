#include "ToySchema/ToySchemaOps.h"
using namespace mlir;
using namespace toy_schema;
#define GET_OP_CLASSES
#include "ToySchema/ToySchemaOps.cpp.inc"
LogicalResult ValidateStringOp::verify() { return success(); }
LogicalResult ValidateRangeOp::verify() { return success(); }
LogicalResult TensorAllocOp::verify() { return success(); }
