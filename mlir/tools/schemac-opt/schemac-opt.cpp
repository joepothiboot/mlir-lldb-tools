#include "ToySchema/ToySchemaDialect.h"
#include "mlir/InitAllDialects.h"
#include "mlir/Tools/mlir-opt/MlirOptMain.h"
int main(int argc, char **argv) {
  mlir::DialectRegistry registry;
  mlir::registerAllDialects(registry);
  registry.insert<toy_schema::ToySchemaDialect>();
  return mlir::asMainReturnCode(mlir::MlirOptMain(argc, argv, "toy_schema opt\n", registry));
}
