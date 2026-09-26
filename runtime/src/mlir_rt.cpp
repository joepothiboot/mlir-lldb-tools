#include "mlir_rt.h"
#include <cstring>
#include <cstdlib>

extern "C" TensorView tensor_alloc(DType dt, uint32_t rank, const int64_t shape[4]) {
  TensorView t; std::memset(&t, 0, sizeof t);
  t.dtype = dt; t.rank = rank; t.layout = LAYOUT_ROW_MAJOR;
  int64_t elems = 1;
  for (uint32_t i = 0; i < rank; ++i) { t.shape[i] = shape[i]; elems *= shape[i]; }
  int64_t stride = 1;
  for (int i = (int)rank - 1; i >= 0; --i) { t.strides[i] = stride; stride *= t.shape[i]; }
  t.data = std::calloc((size_t)elems, 4);
  t.magic = TENSOR_MAGIC;
  return t;
}

extern "C" DspBuffer dsp_alloc(uint64_t frames, uint32_t ch, uint32_t rate) {
  DspBuffer b; std::memset(&b, 0, sizeof b);
  b.frames = frames; b.channels = ch; b.sample_rate = rate;
  b.samples = (float*)std::calloc(frames * ch, sizeof(float));
  b.magic = DSP_MAGIC;
  return b;
}

extern "C" SchemaField* schema_field(SchemaObject* o, const char* name) {
  for (uint32_t i = 0; i < o->field_count; ++i)
    if (std::strcmp(o->fields[i].name, name) == 0) return &o->fields[i];
  return nullptr;
}

extern "C" int schema_validate_string(SchemaField* f, int64_t max_len, RuntimeError* err) {
  if (!f || !f->str_value) return 0;
  if ((int64_t)std::strlen(f->str_value) > max_len) {
    err->kind = 2; err->magic = ERROR_MAGIC; err->message = "string exceeds max length";
    err->source_file = "examples/audioframe.schema"; err->source_line = 2; err->value_id = f->value_id;
    return 0;
  }
  return 1;
}

extern "C" int schema_validate_range(SchemaField* f, int64_t lo, int64_t hi, RuntimeError* err) {
  if (!f) return 0;
  if (f->int_value < lo || f->int_value > hi) {
    err->kind = 2; err->magic = ERROR_MAGIC; err->message = "integer out of range";
    err->source_file = "examples/audioframe.schema"; err->source_line = 3; err->value_id = f->value_id;
    return 0;
  }
  return 1;
}