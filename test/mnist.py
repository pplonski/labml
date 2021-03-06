import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data

from labml import experiment
from labml.configs import option
from labml.helpers.pytorch.datasets.mnist import MNISTConfigs
from labml.helpers.pytorch.device import DeviceConfigs
from labml.helpers.pytorch.seed import SeedConfigs
from labml.helpers.pytorch.train_valid import TrainValidConfigs


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 20, 5, 1)
        self.conv2 = nn.Conv2d(20, 50, 5, 1)
        self.fc1 = nn.Linear(4 * 4 * 50, 500)
        self.fc2 = nn.Linear(500, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2, 2)
        x = x.view(-1, 4 * 4 * 50)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


class SimpleAccuracy:
    def __call__(self, output: torch.Tensor, target: torch.Tensor) -> int:
        pred = output.argmax(dim=1)
        return pred.eq(target).sum().item()


class Configs(MNISTConfigs, DeviceConfigs, SeedConfigs, TrainValidConfigs):
    epochs: int = 10

    is_save_models = True
    model: nn.Module

    learning_rate: float = 2.5e-4
    momentum: float = 0.5

    loss_func = 'cross_entropy_loss'
    accuracy_func = 'simple_accuracy'


@option(Configs.model)
def model(c: Configs):
    return Net().to(c.device)


@option(Configs.accuracy_func)
def simple_accuracy():
    return SimpleAccuracy()


@option(Configs.loss_func)
def cross_entropy_loss():
    return nn.CrossEntropyLoss()


@option(Configs.optimizer)
def sgd_optimizer(c: Configs):
    return optim.SGD(c.model.parameters(), c.learning_rate, c.momentum)


@option(Configs.optimizer)
def adam_optimizer(c: Configs):
    return optim.Adam(c.model.parameters(), c.learning_rate)


def main():
    conf = Configs()
    experiment.create(name='mnist_latest')
    conf.optimizer = 'adam_optimizer'
    conf.cuda_device = 1
    experiment.configs(conf,
                       {},
                       ['set_seed', 'run'])
    experiment.add_pytorch_models(dict(model=conf.model))
    experiment.start()
    conf.run()


if __name__ == '__main__':
    main()
