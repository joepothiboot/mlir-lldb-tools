// Lowers toy_schema ops to llvm.call into the C runtime, PRESERVING location.
// The invariant this file exists to enforce: a lowering may enrich location
// info, never erase it. rewriter.create<>(op->getLoc(), ...) everywhere.
struct ValidateStringLowering
    : public OpConversionPattern<toy_schema::ValidateStringOp> {
  using OpConversionPattern::OpConversionPattern;
  LogicalResult matchAndRewrite(toy_schema::ValidateStringOp op,
                                OpAdaptor adaptor,
                                ConversionPatternRewriter &rw) const override {
    auto loc = op.getLoc();                       // <- carried, not dropped
    auto fn  = getOrInsertRuntimeFn(rw, op, "schema_validate_string",
                                    /*ret=*/rw.getI1Type(),
                                    {adaptor.getValue().getType(),
                                     rw.getI64Type()});
    Value maxLen = rw.create<LLVM::ConstantOp>(loc, rw.getI64Type(),
                                               op.getMaxLenAttr());
    auto call = rw.create<LLVM::CallOp>(loc, fn,
                                        ValueRange{adaptor.getValue(), maxLen});
    rw.replaceOp(op, call.getResult());
    return success();
  }
};