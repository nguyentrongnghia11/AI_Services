
from ..utils.model_loader import model_detect
from ..utils.model_loader import tokenizer_detect
def ToxicDetector (input_text, prefix):
    prefix = 'hate-speech-detection'
    # Add prefix
    prefixed_input_text = prefix + ': ' + input_text

    # Tokenize input text
    input_ids = tokenizer_detect.encode(prefixed_input_text, return_tensors="pt")

    output_ids = model_detect.generate(input_ids, max_length=256)

    output_text = tokenizer_detect.decode(output_ids[0], skip_special_tokens=True)

    return output_text

# Choose 1 from 3 prefixes ['hate-speech-detection', 'toxic-speech-detection', 'hate-spans-detection']



