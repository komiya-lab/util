# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
from transformers import BertTokenizerFast
from transformers.models.bert_japanese.tokenization_bert_japanese import MecabTokenizer

class MecabPreTokenizer(MecabTokenizer):

  def mecab_split(self,i,normalized_string):
    t=str(normalized_string)
    e=0
    z=[]
    for c in self.tokenize(t):
      s=t.find(c,e)
      e=e if s<0 else s+len(c)
      z.append((0,0) if s<0 else (s,e))
    return [normalized_string[s:e] for s,e in z if e>0]
  def pre_tokenize(self,pretok):
    pretok.split(self.mecab_split)

class BertMecabTokenizerFast(BertTokenizerFast):

  def __init__(self,vocab_file,do_lower_case=False,tokenize_chinese_chars=False,**kwargs):
    from tokenizers.pre_tokenizers import PreTokenizer,BertPreTokenizer,Sequence
    super().__init__(vocab_file=vocab_file,do_lower_case=do_lower_case,tokenize_chinese_chars=tokenize_chinese_chars,**kwargs)
    d=kwargs["mecab_kwargs"] if "mecab_kwargs" in kwargs else {"mecab_dic":"ipadic"}
    self._tokenizer.pre_tokenizer=Sequence([PreTokenizer.custom(MecabPreTokenizer(**d)),BertPreTokenizer()])

class ScalarMix(nn.Module):
    r"""
    Computes a parameterised scalar mixture of :math:`N` tensors, :math:`mixture = \gamma * \sum_{k}(s_k * tensor_k)`
    where :math:`s = \mathrm{softmax}(w)`, with :math:`w` and :math:`\gamma` scalar parameters.

    Args:
        n_layers (int):
            The number of layers to be mixed, i.e., :math:`N`.
        dropout (float):
            The dropout ratio of the layer weights.
            If dropout > 0, then for each scalar weight, adjust its softmax weight mass to 0
            with the dropout probability (i.e., setting the unnormalized weight to -inf).
            This effectively redistributes the dropped probability mass to all other weights.
            Default: 0.
    """

    def __init__(self, n_layers: int, dropout: float = 0.0):
        super().__init__()

        self.n_layers = n_layers

        self.weights = nn.Parameter(torch.zeros(n_layers))
        self.gamma = nn.Parameter(torch.tensor([1.0]))
        self.dropout = nn.Dropout(dropout)

    def __repr__(self):
        s = f"n_layers={self.n_layers}"
        if self.dropout.p > 0:
            s += f", dropout={self.dropout.p}"

        return f"{self.__class__.__name__}({s})"

    def forward(self, tensors):
        r"""
        Args:
            tensors (list[~torch.Tensor]):
                :math:`N` tensors to be mixed.

        Returns:
            The mixture of :math:`N` tensors.
        """

        normed_weights = self.dropout(self.weights.softmax(-1))
        weighted_sum = sum(w * h for w, h in zip(normed_weights, tensors))

        return self.gamma * weighted_sum
