import torch
import torch.nn as nn
import torch.nn.functional as F
import pdb
import numpy as np
from os.path import join
from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F


from models.model_utils import *

import sys
#sys.path.append('../1-Hierarchical-Pretraining/')
#sys.path.append('../HIPT_4K/')

#from vision_transformer4k import vit4k_xs
from models.vision_transformer import vit_small






######################################
# 3-Stage HIPT Implementation (With Local-Global Pretraining) #
######################################
class RadVit_LGP_CT(nn.Module):
    def __init__(self, path_input_dim=384,  size_arg = "small", dropout=0.25, n_classes=0,
     pretrain_4k='checkpoint', freeze_4k=False, pretrain_WSI='None', freeze_WSI=False):
        super(RadVit_LGP_FC, self).__init__()
        self.size_dict_path = {"small": [384, 192, 192], "big": [1024, 512, 384]}
        #self.fusion = fusion
        size = self.size_dict_path[size_arg]
        ### Local Aggregation
        self.local_vit = vit_small( in_chans=1)
        if pretrain_4k != 'None':
            print("Loading Pretrained Local VIT model...",)
            
            
            #state_dict = torch.load('../../1-Hierarchical-Pretraining/%.pth' % pretrain_4k, map_location='cpu')['teacher']
            #state_dict = torch.load('Documents/GitHub/HIPT/1-Hierarchical-Pretraining/%s.pth' % pretrain_4k, map_location='cpu')['teacher']
            state_dict = torch.load('/home/shero/Documents/GitHub/HIPT/1-Hierarchical-Pretraining/checkpoint0080.pth', map_location='cpu')['teacher']

            state_dict = {k.replace('module.', ""): v for k, v in state_dict.items()}
            state_dict = {k.replace('backbone.', ""): v for k, v in state_dict.items()}
            missing_keys, unexpected_keys = self.local_vit.load_state_dict(state_dict, strict=False)
            print("Done!")
        if freeze_4k:
            print("Freezing Pretrained Local VIT model")
            for param in self.local_vit.parameters():
                param.requires_grad = False
            print("Done")

        ### Global Aggregation
        self.pretrain_WSI = pretrain_WSI
        if pretrain_WSI != 'None':
            pass
        else:
            self.global_phi = nn.Sequential(nn.Linear(size[0], size[0]), nn.ReLU(), nn.Dropout(0.25))
            self.global_transformer = nn.TransformerEncoder(
                nn.TransformerEncoderLayer(
                    d_model=size[0], nhead=3, dim_feedforward=size[0], dropout=0.25, activation='relu'
                ), 
                num_layers=2
            )
            self.global_attn_pool = Attn_Net_Gated(L=size[0], D=size[0], dropout=0.25, n_classes=1)
            self.global_rho = nn.Sequential(*[nn.Linear(size[0], size[0]), nn.ReLU(), nn.Dropout(0.25)])

        self.classifier = nn.Linear(size[0], n_classes)  if n_classes > 0 else nn.Identity()
        

    def forward(self, mr=None, ct=None, **kwargs):
        ### Local
        #h_4096 = self.local_vit(x_256.unfold(1, 16, 16).transpose(1,2))
        """
        if ct !=None:
            x_256 = ct

        """
        if mr != None:
            x_256 = mr
        h_4096 = self.local_vit(x_256)
        
        ### Global
        if self.pretrain_WSI != 'None':
            h_WSI = self.global_vit(h_4096.unsqueeze(dim=0))
        else:
            h_4096 = self.global_phi(h_4096)
            h_4096 = self.global_transformer(h_4096.unsqueeze(1)).squeeze(1)
            A_4096, h_4096 = self.global_attn_pool(h_4096)  
            A_4096 = torch.transpose(A_4096, 1, 0)
            A_4096 = F.softmax(A_4096, dim=1) 
            h_path = torch.mm(A_4096, h_4096)
            h_WSI = self.global_rho(h_path)

        #logits = self.classifier(h_WSI)
        x = self.classifier(h_WSI)
        #Y_hat = torch.topk(logits, 1, dim = 1)[1]
        #return logits, F.softmax(logits, dim=1), Y_hat, None, None
        return x

    """
    def relocate(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if torch.cuda.device_count() >= 1:
            device_ids = list(range(torch.cuda.device_count()))
            self.local_vit = nn.DataParallel(self.local_vit, device_ids=device_ids).to('cuda:0')
            if self.pretrain_WSI != 'None':
                self.global_vit = nn.DataParallel(self.global_vit, device_ids=device_ids).to('cuda:0')

        if self.pretrain_WSI == 'None':
            self.global_phi = self.global_phi.to(device)
            self.global_transformer = self.global_transformer.to(device)
            self.global_attn_pool = self.global_attn_pool.to(device)
            self.global_rho = self.global_rho.to(device)

        self.classifier = self.classifier.to(device)

    """






######################################
# 3-Stage HIPT Implementation (With Local-Global Pretraining) #
######################################
class RadVit_LGP_MR(nn.Module):
    def __init__(self, path_input_dim=384,  size_arg = "small", dropout=0.25, n_classes=0,
     pretrain_4k='checkpoint', freeze_4k=False, pretrain_WSI='None', freeze_WSI=False):
        super(RadVit_LGP_FC, self).__init__()
        self.size_dict_path = {"small": [384, 192, 192], "big": [1024, 512, 384]}
        #self.fusion = fusion
        size = self.size_dict_path[size_arg]
        ### Local Aggregation
        self.local_vit = vit_small( in_chans=1)
        if pretrain_4k != 'None':
            print("Loading Pretrained Local VIT model...",)
            
            
            #state_dict = torch.load('../../1-Hierarchical-Pretraining/%.pth' % pretrain_4k, map_location='cpu')['teacher']
            #state_dict = torch.load('Documents/GitHub/HIPT/1-Hierarchical-Pretraining/%s.pth' % pretrain_4k, map_location='cpu')['teacher']
            state_dict = torch.load('/home/shero/Documents/GitHub/HIPT/1-Hierarchical-Pretraining/checkpoint0080.pth', map_location='cpu')['teacher']

            state_dict = {k.replace('module.', ""): v for k, v in state_dict.items()}
            state_dict = {k.replace('backbone.', ""): v for k, v in state_dict.items()}
            missing_keys, unexpected_keys = self.local_vit.load_state_dict(state_dict, strict=False)
            print("Done!")
        if freeze_4k:
            print("Freezing Pretrained Local VIT model")
            for param in self.local_vit.parameters():
                param.requires_grad = False
            print("Done")

        ### Global Aggregation
        self.pretrain_WSI = pretrain_WSI
        if pretrain_WSI != 'None':
            pass
        else:
            self.global_phi = nn.Sequential(nn.Linear(size[0], size[0]), nn.ReLU(), nn.Dropout(0.25))
            self.global_transformer = nn.TransformerEncoder(
                nn.TransformerEncoderLayer(
                    d_model=size[0], nhead=3, dim_feedforward=size[0], dropout=0.25, activation='relu'
                ), 
                num_layers=2
            )
            self.global_attn_pool = Attn_Net_Gated(L=size[0], D=size[0], dropout=0.25, n_classes=1)
            self.global_rho = nn.Sequential(*[nn.Linear(size[0], size[0]), nn.ReLU(), nn.Dropout(0.25)])

        self.classifier = nn.Linear(size[0], n_classes)  if n_classes > 0 else nn.Identity()
        

    def forward(self, mr=None, ct=None, **kwargs):
        ### Local
        #h_4096 = self.local_vit(x_256.unfold(1, 16, 16).transpose(1,2))
        """
        if ct !=None:
            x_256 = ct

        """
        if mr != None:
            x_256 = mr
        h_4096 = self.local_vit(x_256)
        
        ### Global
        if self.pretrain_WSI != 'None':
            h_WSI = self.global_vit(h_4096.unsqueeze(dim=0))
        else:
            h_4096 = self.global_phi(h_4096)
            h_4096 = self.global_transformer(h_4096.unsqueeze(1)).squeeze(1)
            A_4096, h_4096 = self.global_attn_pool(h_4096)  
            A_4096 = torch.transpose(A_4096, 1, 0)
            A_4096 = F.softmax(A_4096, dim=1) 
            h_path = torch.mm(A_4096, h_4096)
            h_WSI = self.global_rho(h_path)

        #logits = self.classifier(h_WSI)
        x = self.classifier(h_WSI)
        #Y_hat = torch.topk(logits, 1, dim = 1)[1]
        #return logits, F.softmax(logits, dim=1), Y_hat, None, None
        return x

    """
    def relocate(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if torch.cuda.device_count() >= 1:
            device_ids = list(range(torch.cuda.device_count()))
            self.local_vit = nn.DataParallel(self.local_vit, device_ids=device_ids).to('cuda:0')
            if self.pretrain_WSI != 'None':
                self.global_vit = nn.DataParallel(self.global_vit, device_ids=device_ids).to('cuda:0')

        if self.pretrain_WSI == 'None':
            self.global_phi = self.global_phi.to(device)
            self.global_transformer = self.global_transformer.to(device)
            self.global_attn_pool = self.global_attn_pool.to(device)
            self.global_rho = self.global_rho.to(device)

        self.classifier = self.classifier.to(device)

    """

