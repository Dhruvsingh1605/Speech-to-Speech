
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

torch.cuda.empty_cache()

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,  
    bnb_4bit_use_double_quant=True,  
    bnb_4bit_quant_type="nf4",  
    bnb_4bit_compute_dtype=torch.float16  
)

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen1.5-0.5B",
                                          trust_remote_code=True,)
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen1.5-0.5B",
    trust_remote_code=True,
    quantization_config=bnb_config,
    device_map="auto"
)

def generate(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    with torch.inference_mode():
        out = model.generate(
            **inputs,
            max_new_tokens=32,  
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )
    return tokenizer.decode(out[0], skip_special_tokens=True)