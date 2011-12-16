#! /usr/bin/env python

"""
Questions:

How do we add values like "quality"?
"""

import os
import shutil
import sys

from lab.downward.downward_experiment import DownwardExperiment
from lab.downward.checkouts import Translator, Preprocessor, Planner
from lab.downward.reports.absolute import AbsoluteReport
from lab.downward.reports.ipc import IpcReport
from lab.downward.reports.scatter import ScatterPlotReport
from lab.downward.reports.suite import SuiteReport
from lab.downward.reports.relative import RelativeReport
from lab.environments import LocalEnvironment
from lab.downward import configs
from lab.experiment import Step
from lab import tools


EXPNAME = 'test-exp'
EXPPATH = os.path.join(tools.USER_DIR, 'experiments', EXPNAME)
REPORTS = os.path.join(tools.USER_DIR, 'reports')
REPO = '/home/jendrik/projects/Downward/downward'
ATTRIBUTES = ['cost', 'coverage', 'search_time']
LIMITS = {'search_time': 900}
COMBINATIONS = [(Translator(repo=REPO), Preprocessor(repo=REPO), Planner(repo=REPO))]
ENV = LocalEnvironment()

exp = DownwardExperiment(path=EXPPATH, env=ENV, repo=REPO,
                         combinations=COMBINATIONS, limits=LIMITS)

exp.add_suite('gripper:prob01.pddl')
exp.add_suite('depot:pfile1')

exp.add_config(*configs.pdb_max_states(1000))
exp.add_config('yY', configs.yY)
exp.add_config('lama', configs.lama)
exp.add_config('multiple', configs.multiple_plans)
exp.add_config('iterated', configs.iterated_search)
exp.add_portfolio(os.path.join(REPO, 'src/search/downward-seq-sat-fdss-1.py'))
exp.add_portfolio('/home/jendrik/projects/Downward/fastr/new-scripts/portfolios/uniform.py')

exp.steps.insert(5, Step('clear-results', shutil.rmtree, exp.eval_dir))

def lama_and_yY(run):
    return run['config'] in ['WORK-lama', 'WORK-yY']

abs_domain_report_file = os.path.join(REPORTS, '%s-abs-d.html' % EXPNAME)
abs_problem_report_file = os.path.join(REPORTS, '%s-abs-p.html' % EXPNAME)
exp.add_step(Step('report-abs-d', AbsoluteReport('domain', attributes=ATTRIBUTES), exp.eval_dir, abs_domain_report_file))
exp.add_step(Step('report-abs-p', AbsoluteReport('problem', attributes=ATTRIBUTES), exp.eval_dir, abs_problem_report_file))
#exp.add_step(Step('report-ipc', IpcReport(attributes=['coverage']), exp.eval_dir, os.path.join(REPORTS, 'ipc.tex')))
#exp.add_step(Step('report-scatter', ScatterPlotReport(attributes=['expansions'], filters=[lama_and_yY]), exp.eval_dir, os.path.join(REPORTS, 'scatter.png')))
#exp.add_step(Step('report-suite', SuiteReport(), exp.eval_dir, os.path.join(REPORTS, 'suite.py')))
#exp.add_step(Step('report-rel', RelativeReport('problem', filters=[lama_and_yY]), exp.eval_dir, os.path.join(REPORTS, 'rel.html')))

# exp.steps is a list that can be manipulated:
# steps can be removed, appended, replaced and inserted
#exp.steps.insert(6, Step('report-abs', AbsoluteReport('domain', attributes=['coverage']), exp.eval_dir, 'report-abs.html'))
#del exp.steps[7]

# Compress the experiment directory
#exp.add_step(Step('zip-exp-dir', Call, ['tar', '-cvzf', exp.path + '.tar.gz', exp.path]))

def copy_results():
    dest = os.path.join(os.path.expanduser('~'), '.public_html/',
                        os.path.basename(abs_domain_report_file))
    shutil.copy2(abs_domain_report_file, dest)

# Copy the results
exp.add_step(Step('copy-results', copy_results))

# Remove the experiment directory
#exp.add_step(Step('remove-exp-dir', shutil.rmtree, exp.path))

# This method parses the commandline. We assume this file is called exp.py.
# Supported styles:
# ./exp.py 1
# ./exp.py 4 5 6
# ./exp.py next
# ./exp.py rest      # runs all remaining steps
exp()