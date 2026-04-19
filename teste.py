pip install gguf
python3 -c "
import gguf
reader = gguf.GGUFReader('outputs/cycle-1/gguf/oci-specialist-fp16.gguf')
print('Arquitetura:', reader.arch_name)
for tensor in reader.tensors:
    if 'f16' in tensor.dtype.lower() or tensor.dtype == 1:  # 1=F16
        print(f'Tensor FP16: {tensor.name}')
"
