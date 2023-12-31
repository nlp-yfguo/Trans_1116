#encoding: utf-8

from torch import nn

from modules.base import ResidueCombiner
from transformer.AGG.HierEncoder import Encoder as EncoderBase
from transformer.Encoder import EncoderLayer as EncoderLayerBase
from utils.fmt.parser import parse_none

from cnfg.ihyp import *

class EncoderLayer(nn.Module):

	def __init__(self, isize, fhsize=None, dropout=0.0, attn_drop=0.0, act_drop=None, num_head=8, ahsize=None, num_sub=1, comb_input=True, **kwargs):

		_ahsize = parse_none(ahsize, isize)

		_fhsize = _ahsize * 4 if fhsize is None else fhsize

		super(EncoderLayer, self).__init__()

		self.nets = nn.ModuleList([EncoderLayerBase(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize) for i in range(num_sub)])

		self.combiner = ResidueCombiner(isize, num_sub + 1 if comb_input else num_sub, _fhsize)

		self.comb_input = comb_input

	def forward(self, inputs, mask=None, **kwargs):

		out = inputs
		outs = [out] if self.comb_input else []
		for net in self.nets:
			out = net(out, mask)
			outs.append(out)

		return self.combiner(*outs)

class FEncoderLayer(nn.Module):

	def __init__(self, isize, fhsize=None, dropout=0.0, attn_drop=0.0, act_drop=None, num_head=8, ahsize=None, **kwargs):

		_ahsize = parse_none(ahsize, isize)

		_fhsize = _ahsize * 4 if fhsize is None else fhsize

		super(FEncoderLayer, self).__init__()

		self.nets = nn.ModuleList([EncoderLayer(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize, num_sub=2, comb_input=False), EncoderLayer(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize, num_sub=2, comb_input=True)])

	def forward(self, inputs, mask=None, **kwargs):

		out = inputs
		for net in self.nets:
			out = net(out, mask)

		return out

class SEncoderLayer(nn.Module):

	def __init__(self, isize, fhsize=None, dropout=0.0, attn_drop=0.0, act_drop=None, num_head=8, ahsize=None, **kwargs):

		_ahsize = parse_none(ahsize, isize)

		_fhsize = _ahsize * 4 if fhsize is None else fhsize

		super(SEncoderLayer, self).__init__()

		self.nets = nn.ModuleList([EncoderLayer(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize, num_sub=2, comb_input=False), EncoderLayerBase(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize), EncoderLayerBase(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize)])
		self.combiner = ResidueCombiner(isize, 4, _fhsize)

	def forward(self, inputs, mask=None, **kwargs):

		out = inputs
		outs = [out]
		for net in self.nets:
			out = net(out, mask)
			outs.append(out)

		return self.combiner(*outs)

class Encoder(EncoderBase):

	def __init__(self, isize, nwd, num_layer, fhsize=None, dropout=0.0, attn_drop=0.0, act_drop=None, num_head=8, xseql=cache_len_default, ahsize=None, norm_output=False, num_sub=1, **kwargs):

		_ahsize = parse_none(ahsize, isize)

		_fhsize = _ahsize * 4 if fhsize is None else fhsize

		super(Encoder, self).__init__(isize, nwd, 2, fhsize=_fhsize, dropout=dropout, attn_drop=attn_drop, act_drop=act_drop, num_head=num_head, xseql=xseql, ahsize=_ahsize, norm_output=norm_output, **kwargs)

		self.nets = nn.ModuleList([FEncoderLayer(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize), SEncoderLayer(isize, _fhsize, dropout, attn_drop, act_drop, num_head, _ahsize)])
