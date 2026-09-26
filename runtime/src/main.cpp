#include "mlir_rt.h"
#include <cstdio>
#include <cstring>

bool AudioFrame_validate(SchemaObject*, RuntimeError*);

extern "C" __attribute__((noinline, used)) void mlir_debug_checkpoint() {
  __asm__ __volatile__("" ::: "memory");
}

int main() {
  static SchemaField fields[] = {
    {"name",    0, 0, {0, 64, 0, 1},    2, "frame-alpha", 0},
    {"rate",    1, 0, {8000, 192000, 1, 1}, 4, nullptr, 48000},
    {"window",  2, 0, {0, 0, 0, 0},     6, nullptr, 0},
    {"samples", 3, 0, {0, 0, 0, 0},     8, nullptr, 0},
  };
  SchemaObject obj{"AudioFrame", fields, 4, 0, SCHEMA_MAGIC, 0};
  RuntimeError err{}; err.magic = ERROR_MAGIC;

  TensorView win = tensor_alloc(DT_F32, 2, (int64_t[4]){16, 64, 0, 0});
  DspBuffer  buf = dsp_alloc(1024, 2, 48000);

  mlir_debug_checkpoint();
  bool ok = AudioFrame_validate(&obj, &err);
  mlir_debug_checkpoint();
  return 0;
}