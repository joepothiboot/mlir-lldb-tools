include "mlir/IR/OpBase.td"
def ToySchema_Dialect : Dialect {
  let name = "toy_schema";
  let cppNamespace = "::toy_schema";
  let useDefaultTypePrinterParser = 1;
}
