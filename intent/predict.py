from pickle import TRUE
from torch.hub import load_state_dict_from_url
import torchtext.transforms as T
import torch
import torchtext.functional as F
import numpy as np

DEVICE = torch.device('cpu')

padding_idx = 1
bos_idx = 0
eos_idx = 2
max_seq_len = 256
vocab_path = r"https://download.pytorch.org/models/text/xlmr.vocab.pt"
spm_model_path = r"https://download.pytorch.org/models/text/xlmr.sentencepiece.bpe.model"

text_transform = T.Sequential(
    T.SentencePieceTokenizer(spm_model_path),
    T.VocabTransform(load_state_dict_from_url(vocab_path)),
    T.Truncate(max_seq_len - 2),
    T.AddToken(token=bos_idx, begin=True),
    T.AddToken(token=eos_idx, begin=False),
)

model = torch.load("D:\\projects\\python\\test\\src\\intent\\model.pt")
model.to(DEVICE)


def predict(input: str, threhold=5):
    with torch.no_grad():
        input = text_transform(input)

        input = F.to_tensor([input], padding_value=padding_idx).to(DEVICE)

        output = model(input).data.tolist()

        return np.argmax(output), max(output[0]) > threhold
