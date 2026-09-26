#pragma once
#include <stdint.h>
#include <stddef.h>

#define TENSOR_MAGIC 0x544E5352u
#define DSP_MAGIC    0x44535042u
#define SCHEMA_MAGIC 0x53434D41u
#define ERROR_MAGIC  0x45525221u

typedef enum { DT_F32=0, DT_F64=1, DT_I32=2, DT_I64=3, DT_I8=4 } DType;
typedef enum { LAYOUT_ROW_MAJOR=0 } Layout;

typedef struct { void* data; uint32_t dtype; uint32_t rank; int64_t shape[4]; int64_t strides[4]; uint32_t layout; uint32_t magic; } TensorView;
typedef struct { float* samples; uint64_t frames; uint32_t channels; uint32_t sample_rate; uint64_t write_cursor; uint32_t magic; uint32_t _pad; } DspBuffer;
typedef struct { int64_t min; int64_t max; uint32_t has_min; uint32_t has_max; } ConstraintSet;
typedef struct { const char* name; uint32_t kind; uint32_t flags; ConstraintSet constraints; uint32_t value_id; const char* str_value; int64_t int_value; } SchemaField;
typedef struct { const char* schema_name; SchemaField* fields; uint32_t field_count; uint32_t validated_mask; uint32_t magic; uint32_t _pad; } SchemaObject;
typedef struct { uint32_t kind; uint32_t magic; const char* message; const char* source_file; uint32_t source_line; uint32_t value_id; } RuntimeError;

#ifdef __cplusplus
extern "C" {
#endif
TensorView tensor_alloc(DType dt, uint32_t rank, const int64_t shape[4]);
DspBuffer  dsp_alloc(uint64_t frames, uint32_t channels, uint32_t rate);
SchemaField* schema_field(SchemaObject* o, const char* name);
int schema_validate_string(SchemaField* f, int64_t max_len, RuntimeError* err);
int schema_validate_range (SchemaField* f, int64_t lo, int64_t hi, RuntimeError* err);
#ifdef __cplusplus
}
#endif