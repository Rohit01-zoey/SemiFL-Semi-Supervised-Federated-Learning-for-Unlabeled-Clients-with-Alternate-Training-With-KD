import argparse
import itertools

parser = argparse.ArgumentParser(description='config')
parser.add_argument('--run', default='train', type=str)
parser.add_argument('--num_gpus', default=4, type=int)
parser.add_argument('--world_size', default=1, type=int)
parser.add_argument('--init_seed', default=0, type=int)
parser.add_argument('--round', default=4, type=int)
parser.add_argument('--experiment_step', default=1, type=int)
parser.add_argument('--num_experiments', default=1, type=int)
parser.add_argument('--resume_mode', default=0, type=int)
parser.add_argument('--data', default=None, type=str)
parser.add_argument('--model', default=None, type=str)
parser.add_argument('--mode', default=None, type=str)
parser.add_argument('--split_round', default=65535, type=int)
args = vars(parser.parse_args())


def make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments, resume_mode,
                  control_name):
    control_names = []
    for i in range(len(control_name)):
        control_names.extend(list('_'.join(x) for x in itertools.product(*control_name[i])))
    control_names = [control_names]
    controls = script_name + data_names + model_names + init_seeds + world_size + num_experiments + resume_mode + \
               control_names
    controls = list(itertools.product(*controls))
    return controls


def main():
    run = args['run']
    num_gpus = args['num_gpus']
    world_size = args['world_size']
    round = args['round']
    experiment_step = args['experiment_step']
    init_seed = args['init_seed']
    num_experiments = args['num_experiments']
    resume_mode = args['resume_mode']
    mode = args['mode']
    split_round = args['split_round']
    gpu_ids = [','.join(str(i) for i in list(range(x, x + world_size))) for x in list(range(0, num_gpus, world_size))]
    init_seeds = [list(range(init_seed, init_seed + num_experiments, experiment_step))]
    world_size = [[world_size]]
    num_experiments = [[experiment_step]]
    resume_mode = [[resume_mode]]
    modename = '{}_{}'.format(run, mode)
    if mode == 'fs':
        script_name = [['{}_classifier.py'.format(run)]]
        control_name = [[['fs']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        data_names = [['SVHN']]
        model_names = [['wresnet28x2']]
        svhn_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                      resume_mode, control_name)
        data_names = [['CIFAR100']]
        model_names = [['wresnet28x8']]
        cifar100_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                          resume_mode, control_name)
        controls = cifar10_controls + svhn_controls + cifar100_controls
    elif mode == 'ps':
        script_name = [['{}_classifier.py'.format(run)]]
        control_name = [[['250', '4000']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size,
                                         num_experiments,
                                         resume_mode, control_name)
        control_name = [[['250', '1000']]]
        data_names = [['SVHN']]
        model_names = [['wresnet28x2']]
        svhn_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                      resume_mode, control_name)
        control_name = [[['2500', '10000']]]
        data_names = [['CIFAR100']]
        model_names = [['wresnet28x8']]
        cifar100_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                          resume_mode, control_name)
        controls = cifar10_controls + svhn_controls + cifar100_controls
    elif mode == 'fl':
        script_name = [['{}_classifier_fl.py'.format(run)]]
        control_name = [
            [['fs'], ['sup'], ['100'], ['0.1'], ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-0'],
             ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        control_name = [
            [['fs'], ['sup'], ['100'], ['0.1'], ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-0'],
             ['0.5'], ['1']]]
        data_names = [['SVHN']]
        model_names = [['wresnet28x2']]
        svhn_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                      resume_mode, control_name)
        control_name = [
            [['fs'], ['sup'], ['100'], ['0.1'], ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-0'],
             ['0.5'], ['1']]]
        data_names = [['CIFAR100']]
        model_names = [['wresnet28x8']]
        cifar100_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                          resume_mode, control_name)
        controls = cifar10_controls + svhn_controls + cifar100_controls
    elif mode == 'ssfl':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [
            [['250', '4000'], ['fix@0.95-mix'], ['100'], ['0.1'],
             ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        control_name = [
            [['250', '1000'], ['fix@0.95-mix'], ['100'], ['0.1'],
             ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1']]]
        data_names = [['SVHN']]
        model_names = [['wresnet28x2']]
        svhn_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                      resume_mode, control_name)
        control_name = [
            [['2500', '10000'], ['fix@0.95-mix'], ['100'], ['0.1'],
             ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1']]]
        data_names = [['CIFAR100']]
        model_names = [['wresnet28x8']]
        cifar100_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                          resume_mode, control_name)
        controls = cifar10_controls + svhn_controls + cifar100_controls
    elif mode == 'frgd':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [
            [['250', '4000'], ['fix@0.95-frgd'], ['100'], ['0.1'],
             ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1'], ['0']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        control_name = [
            [['250', '1000'], ['fix@0.95-frgd'], ['100'], ['0.1'],
             ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1'], ['0']]]
        data_names = [['SVHN']]
        model_names = [['wresnet28x2']]
        svhn_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                      resume_mode, control_name)
        control_name = [[['2500', '10000'], ['fix@0.95-frgd'], ['100'], ['0.1'],
                         ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1'], ['0']]]
        data_names = [['CIFAR100']]
        model_names = [['wresnet28x8']]
        cifar100_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                          resume_mode, control_name)
        controls = cifar10_controls + svhn_controls + cifar100_controls
    elif mode == 'fmatch':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [[['250', '4000'], ['fix@0.95-fmatch'], ['100'], ['0.1'],
                         ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['decwresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        control_name = [[['250', '1000'], ['fix@0.95-fmatch'], ['100'], ['0.1'],
                         ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1'], ['1']]]
        data_names = [['SVHN']]
        model_names = [['decwresnet28x2']]
        svhn_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                      resume_mode, control_name)
        control_name = [[['2500', '10000'], ['fix@0.95-fmatch'], ['100'], ['0.1'],
                         ['iid', 'non-iid-d-0.3', 'non-iid-d-0.1', 'non-iid-l-2'], ['5-5'], ['0.5'], ['1'], ['1']]]
        data_names = [['CIFAR100']]
        model_names = [['decwresnet28x8']]
        cifar100_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                          resume_mode, control_name)
        controls = cifar10_controls + svhn_controls + cifar100_controls
    elif mode == 'tau':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [[['250', '4000'], ['fix@0-mix', 'fix@0.5-mix', 'fix@0.99-mix'], ['100'], ['0.1'],
                         ['iid'], ['5-5'], ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        controls = cifar10_controls
    elif mode == 'mix':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [[['250', '4000'], ['fix@0.95'], ['100'], ['0.1'], ['iid'], ['5-5'], ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        controls = cifar10_controls
    elif mode == 'lu':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [
            [['250', '4000'], ['fix@0.95-mix'], ['100'], ['0.1'], ['iid'], ['0.001-0.001', '0.1-0.1', '1-1', '10-10'],
             ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        controls = cifar10_controls
    elif mode == 'lu-s':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [
            [['250', '4000'], ['fix@0.95-mix'], ['100'], ['0.1'], ['iid'], ['0.001-5', '0.1-5', '1-5', '10-5'],
             ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        controls = cifar10_controls
    elif mode == 'gm':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [
            [['250', '4000'], ['fix@0.95-mix'], ['100'], ['0.1'], ['iid'], ['5-5'], ['0', '0.9'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        controls = cifar10_controls
    elif mode == 'sbn':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [
            [['250', '4000'], ['fix@0.95-mix'], ['100'], ['0.1'], ['iid'], ['5-5'], ['0.5'], ['0']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls = make_controls(script_name, data_names, model_names, init_seeds, world_size, num_experiments,
                                         resume_mode, control_name)
        controls = cifar10_controls
    elif mode == 'alternate':
        script_name = [['{}_classifier_ssfl.py'.format(run)]]
        control_name = [[['250', '4000'], ['fix@0.95-batch'], ['100'], ['0.1'], ['iid'],
                         ['0.001-0.001', '0.1-0.1', '1-1', '5-5', '10-10'], ['0.5'], ['1']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls_1 = make_controls(script_name, data_names, model_names, init_seeds, world_size,
                                           num_experiments, resume_mode, control_name)
        control_name = [[['4000'], ['fix@0.95', 'fix@0.95-batch'], ['100'], ['0.1'], ['iid'],
                         ['0.001-0.001', '0.1-0.1', '1-1', '5-5', '10-10'], ['0.5'], ['1'], ['0']]]
        data_names = [['CIFAR10']]
        model_names = [['wresnet28x2']]
        cifar10_controls_2 = make_controls(script_name, data_names, model_names, init_seeds, world_size,
                                           num_experiments, resume_mode, control_name)
        controls = cifar10_controls_1 + cifar10_controls_2
    else:
        raise ValueError('Not valid mode')
    s = '#!/bin/bash\n'
    j = 1
    k = 1
    for i in range(len(controls)):
        controls[i] = list(controls[i])
        s = s + 'CUDA_VISIBLE_DEVICES=\"{}\" python {} --data_name {} --model_name {} --init_seed {} ' \
                '--world_size {} --num_experiments {} --resume_mode {} --control_name {}&\n'.format(
            gpu_ids[i % len(gpu_ids)], *controls[i])
        if i % round == round - 1:
            s = s[:-2] + '\nwait\n'
            if j % split_round == 0:
                print(s)
                run_mode = open('./{}_{}.sh'.format(modename, k), 'w')
                run_mode.write(s)
                run_mode.close()
                s = '#!/bin/bash\n'
                k = k + 1
            j = j + 1
    if s != '#!/bin/bash\n':
        if s[-5:-1] != 'wait':
            s = s + 'wait\n'
        print(s)
        run_mode = open('./{}_{}.sh'.format(modename, k), 'w')
        run_mode.write(s)
        run_mode.close()
    return


if __name__ == '__main__':
    main()
