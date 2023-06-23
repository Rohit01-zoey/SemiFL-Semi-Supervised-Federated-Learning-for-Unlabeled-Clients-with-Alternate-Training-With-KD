import torch
import torch.nn as nn
import torch.nn.functional as F
from .utils import init_param, make_batchnorm, loss_fn, kld_loss
from config import cfg


class Block(nn.Module):
    expansion = 1

    def __init__(self, in_planes, planes, stride):
        super(Block, self).__init__()
        self.n1 = nn.BatchNorm2d(in_planes)
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.n2 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=1, padding=1, bias=False)
        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1, stride=stride, bias=False)

    def forward(self, x):
        out = F.relu(self.n1(x))
        shortcut = self.shortcut(out) if hasattr(self, 'shortcut') else x
        out = self.conv1(out)
        out = self.conv2(F.relu(self.n2(out)))
        out += shortcut
        return out


class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, in_planes, planes, stride):
        super(Bottleneck, self).__init__()
        self.n1 = nn.BatchNorm2d(in_planes)
        self.conv1 = nn.Conv2d(in_planes, planes, kernel_size=1, bias=False)
        self.n2 = nn.BatchNorm2d(planes)
        self.conv2 = nn.Conv2d(planes, planes, kernel_size=3, stride=stride, padding=1, bias=False)
        self.n3 = nn.BatchNorm2d(planes)
        self.conv3 = nn.Conv2d(planes, self.expansion * planes, kernel_size=1, bias=False)

        if stride != 1 or in_planes != self.expansion * planes:
            self.shortcut = nn.Conv2d(in_planes, self.expansion * planes, kernel_size=1, stride=stride, bias=False)

    def forward(self, x):
        out = F.relu(self.n1(x))
        shortcut = self.shortcut(out) if hasattr(self, 'shortcut') else x
        out = self.conv1(out)
        out = self.conv2(F.relu(self.n2(out)))
        out = self.conv3(F.relu(self.n3(out)))
        out += shortcut
        return out


class ResNet(nn.Module):
    def __init__(self, data_shape, hidden_size, block, num_blocks, target_size):
        super().__init__()
        self.in_planes = hidden_size[0]
        self.conv1 = nn.Conv2d(data_shape[0], hidden_size[0], kernel_size=3, stride=1, padding=1, bias=False)
        self.layer1 = self._make_layer(block, hidden_size[0], num_blocks[0], stride=1)
        self.layer2 = self._make_layer(block, hidden_size[1], num_blocks[1], stride=2)
        self.layer3 = self._make_layer(block, hidden_size[2], num_blocks[2], stride=2)
        self.layer4 = self._make_layer(block, hidden_size[3], num_blocks[3], stride=2)
        self.n4 = nn.BatchNorm2d(hidden_size[3] * block.expansion)
        self.linear = nn.Linear(hidden_size[3] * block.expansion, target_size)

    def _make_layer(self, block, planes, num_blocks, stride):
        strides = [stride] + [1] * (num_blocks - 1)
        layers = []
        for stride in strides:
            layers.append(block(self.in_planes, planes, stride))
            self.in_planes = planes * block.expansion
        return nn.Sequential(*layers)

    def f(self, x):
        x = self.conv1(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        x = F.relu(self.n4(x))
        x = F.adaptive_avg_pool2d(x, 1)
        x = x.view(x.size(0), -1)
        x = self.linear(x)
        return x

    def forward(self, input):
        output = {}
        output['target'] = self.f(input['data'])
        if 'loss_mode' in input:
            if 'sup' in input['loss_mode']:
                output['loss'] = loss_fn(output['target'], input['target'])
            elif 'fix' in input['loss_mode'] and 'mix' not in input['loss_mode'] and 'kd' not in input['loss_mode']:
                aug_output = self.f(input['aug'])
                output['loss'] = loss_fn(aug_output, input['target'].detach())
            elif 'fix' in input['loss_mode'] and 'mix' in input['loss_mode'] and 'kd' not in input['loss_mode']:
                aug_output = self.f(input['aug'])
                output['loss'] = loss_fn(aug_output, input['target'].detach())
                mix_output = self.f(input['mix_data'])
                output['loss'] += input['lam'] * loss_fn(mix_output, input['mix_target'][:, 0].detach()) + (
                        1 - input['lam']) * loss_fn(mix_output, input['mix_target'][:, 1].detach())
                
            elif 'kd' in input['loss_mode'] and 'fix' not in input['loss_mode'] and 'mix' not in input['loss_mode']:
                output['loss'] = kld_loss(output['target'], input['target'])
            elif 'kd' in input['loss_mode'] and 'fix' in input['loss_mode'] and 'mix' not in input['loss_mode']:
                aug_output = self.f(input['aug'])
                output['loss'] = kld_loss(aug_output, input['target'].detach())
            elif 'kd' in input['loss_mode'] and 'fix' in input['loss_mode'] and 'mix' in input['loss_mode']:
                aug_output = self.f(input['aug'])
                output['loss'] = kld_loss(aug_output, input['target'].detach())
                mix_output = self.f(input['mix_data'])
                #print("wresent28x2 line 105: ", mix_output.shape, input['mix_target'].shape)
                output['loss'] += input['lam'] * kld_loss(mix_output, input['mix_target'][:, :, 0].detach()) + (
                        1 - input['lam']) * kld_loss(mix_output, input['mix_target'][:, :, 1].detach()) #! changed the indexing to include batches in the future
        else:
            if not torch.any(input['target'] == -1):
                output['loss'] = loss_fn(output['target'], input['target'])
        return output


def resnet9(momentum=None, track=False):
    data_shape = cfg['data_shape']
    target_size = cfg['target_size']
    hidden_size = cfg['resnet9']['hidden_size']
    model = ResNet(data_shape, hidden_size, Block, [1, 1, 1, 1], target_size)
    model.apply(init_param)
    model.apply(lambda m: make_batchnorm(m, momentum=momentum, track_running_stats=track))
    return model


def resnet18(momentum=None, track=False):
    data_shape = cfg['data_shape']
    target_size = cfg['target_size']
    hidden_size = cfg['resnet18']['hidden_size']
    model = ResNet(data_shape, hidden_size, Block, [2, 2, 2, 2], target_size)
    model.apply(init_param)
    model.apply(lambda m: make_batchnorm(m, momentum=momentum, track_running_stats=track))
    return model