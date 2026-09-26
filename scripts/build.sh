# scripts/build.sh (excerpt)
schemac emit-mlir examples/audioframe.schema -o build/audioframe.mlir
build/mlir/bin/schemac-opt build/audioframe.mlir \
    --toy-schema-fold-constraints --toy-schema-elim-redundant \
    --mlir-print-debuginfo -o build/audioframe.opt.mlir
build/mlir/bin/schemac-opt build/audioframe.opt.mlir \
    --toy-schema-to-llvm --mlir-print-debuginfo -o build/audioframe.llvm.mlir
mlir-translate --mlir-to-llvmir build/audioframe.llvm.mlir -o build/audioframe.ll
schemac collect-metadata --mlir build/audioframe.opt.mlir \
    --llvm-ir build/audioframe.ll --cpp build/generated/audioframe_validate.cpp \
    -o build/metadata.json --verify-provenance