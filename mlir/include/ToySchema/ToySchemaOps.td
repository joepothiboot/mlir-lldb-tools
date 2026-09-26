
---

## Stage 3 — real MLIR dialect (Option A) + full mapping

### `mlir/include/ToySchema/ToySchemaOps.td`

```tablegen
#ifndef TOYSCHEMA_OPS
#define TOYSCHEMA_OPS
include "ToySchema/ToySchemaDialect.td"
include "mlir/Interfaces/SideEffectInterfaces.td"
include "mlir/IR/BuiltinTypes.td"

class ToySchema_Op<string mnemonic, list<Trait> traits = []>
    : Op<ToySchema_Dialect, mnemonic, traits>;

def ToySchema_FieldRefOp : ToySchema_Op<"field_ref", [Pure]> {
  let summary = "Reference a named field of a schema object.";
  let arguments = (ins AnyType:$object, StrAttr:$field_name);
  let results   = (outs AnyType:$result);
  let assemblyFormat = "$object `[` $field_name `]` attr-dict "
                       "`:` type($object) `->` type($result)";
}

def ToySchema_ValidateStringOp : ToySchema_Op<"validate_string"> {
  let summary = "Validate a string field against a max-length constraint.";
  let arguments = (ins AnyType:$value, I64Attr:$max_len);
  let results   = (outs I1:$ok);
  let assemblyFormat = "$value `,` `max` `=` $max_len attr-dict `:` type($value)";
}

def ToySchema_ValidateRangeOp : ToySchema_Op<"validate_range"> {
  let arguments = (ins AnyType:$value, I64Attr:$min, I64Attr:$max);
  let results   = (outs I1:$ok);
}

def ToySchema_TensorAllocOp : ToySchema_Op<"tensor_alloc"> {
  let arguments = (ins I64ArrayAttr:$shape, StrAttr:$dtype);
  let results   = (outs AnyType:$tensor);
}

def ToySchema_DspAllocOp : ToySchema_Op<"dsp_alloc"> {
  let arguments = (ins I64Attr:$frames, I64Attr:$channels, I64Attr:$sample_rate);
  let results   = (outs AnyType:$buffer);
}
#endif
