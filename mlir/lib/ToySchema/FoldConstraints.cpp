#include "ToySchema/ToySchemaOps.h"
#include "mlir/Pass/Pass.h"
using namespace mlir;
namespace {
struct FoldConstraintsPass : public mlir::PassWrapper<FoldConstraintsPass, mlir::OperationPass<mlir::ModuleOp>> {
  MLIR_EXPLICIT_INTERNAL_INLINE_TYPE_ID(FoldConstraintsPass)
  void runOnOperation() override {}
};
}
