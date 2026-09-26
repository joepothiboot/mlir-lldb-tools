#include "mlir_rt.h"

bool AudioFrame_validate(SchemaObject* obj, RuntimeError* err) {
    bool __ok = true;
    SchemaObject* __mlir_v0 = obj;
    SchemaField* __mlir_v1 = schema_field(obj, "name");
    bool __mlir_v2 = schema_validate_string(__mlir_v1, 64, err);
    __ok = __ok && __mlir_v2;
    SchemaField* __mlir_v3 = schema_field(obj, "rate");
    bool __mlir_v4 = schema_validate_range(__mlir_v3, 8000LL, 192000LL, err);
    __ok = __ok && __mlir_v4;
    SchemaField* __mlir_v5 = schema_field(obj, "window");
    TensorView __mlir_v6 = tensor_alloc(DT_F32, 2, (int64_t[4]){16, 64, 0, 0});
    SchemaField* __mlir_v7 = schema_field(obj, "samples");
    DspBuffer __mlir_v8 = dsp_alloc(1024, 2, 48000);
    return __ok;
}