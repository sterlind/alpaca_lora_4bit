import os
import sys
sys.path.insert(0, './repository/transformers/src')
sys.path.insert(0, './repository/GPTQ-for-LLaMa')
sys.path.insert(0, './repository/peft/src')
import time
import torch
from autograd_4bit import load_llama_model_4bit_low_ram
config_path = './llama-13b-4bit/'
model_path = './llama-13b-4bit.pt'
model, tokenizer = load_llama_model_4bit_low_ram(config_path, model_path)

print('Fitting 4bit scales and zeros to half')
for n, m in model.named_modules():
    if '4bit' in str(type(m)):
        m.zeros = m.zeros.half()
        m.scales = m.scales.half()

prompt = '''I think the meaning of life is'''
batch = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
batch = {k: v.cuda() for k, v in batch.items()}

start = time.time()
with torch.no_grad():
    generated = model.generate(inputs=batch["input_ids"],
                               do_sample=True, use_cache=True,
                               repetition_penalty=1.1,
                               max_new_tokens=20,
                               temperature=0.9,
                               top_p=0.95,
                               top_k=40,
                               return_dict_in_generate=True,
                               output_attentions=False,
                               output_hidden_states=False,
                               output_scores=False)
result_text = tokenizer.decode(generated['sequences'].cpu().tolist()[0])
end = time.time()
print(result_text)
print(end - start)
