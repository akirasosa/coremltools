# Copyright (c) 2017, Apple Inc. All rights reserved.
#
# Use of this source code is governed by a BSD-3-clause license that can be
# found in the LICENSE.txt file or at https://opensource.org/licenses/BSD-3-Clause

import itertools
from nose.plugins.attrib import attr
import pandas as pd
import unittest

from coremltools._deps import HAS_SKLEARN
from coremltools.models.utils import evaluate_classifier
if HAS_SKLEARN:
    from sklearn.datasets import load_boston
    from sklearn.ensemble import GradientBoostingClassifier
    from coremltools.converters import sklearn as skl_converter

@unittest.skipIf(not HAS_SKLEARN, 'Missing sklearn. Skipping tests.')
class BoostedTreeClassificationBostonHousingScikitNumericTest(unittest.TestCase):
    """
    Unit test class for testing scikit-learn converter and running both models
    """
    @classmethod
    def setUpClass(self):
        """
        Set up the unit test by loading the dataset and training a model.
        """
        from sklearn.datasets import load_boston

        # Load data and train model
        scikit_data = load_boston()
        self.scikit_data = scikit_data
        self.X = scikit_data.data.astype('f').astype('d') ## scikit-learn downcasts data
        self.target = 1 * (scikit_data['target'] > scikit_data['target'].mean())
        self.feature_names = scikit_data.feature_names
        self.output_name = 'target'

    def _check_metrics(self, metrics, params = {}):
        self.assertEquals(metrics['num_errors'], 0, msg = 'Failed case %s. Results %s' % (params, metrics))

    def _train_convert_evaluate(self, **scikit_params):
        """
        Train a scikit-learn model, convert it and then evaluate it with CoreML
        """
        scikit_model = GradientBoostingClassifier(random_state = 1, **scikit_params)
        scikit_model.fit(self.X, self.target)
        
        # Convert the model
        spec = skl_converter.convert(scikit_model, self.feature_names, self.output_name)
        
        # Get predictions
        df = pd.DataFrame(self.X, columns=self.feature_names)
        df['prediction'] = scikit_model.predict(self.X)
        
        # Evaluate it
        metrics = evaluate_classifier(spec, df)
        return metrics

@unittest.skipIf(not HAS_SKLEARN, 'Missing sklearn. Skipping tests.')
class BoostedTreeBinaryClassificationBostonHousingScikitNumericTest(
           BoostedTreeClassificationBostonHousingScikitNumericTest):

    def test_simple_binary_classifier(self):
        metrics = self._train_convert_evaluate()
        self._check_metrics(metrics)

    @attr('slow')
    def test_binary_classifier_stress_test(self):

        options = dict(
               max_depth = [1, 10, None],
               min_samples_split = [2, 0.5],
               min_samples_leaf = [1, 5],
               min_weight_fraction_leaf = [0.0, 0.5],
               max_features = [None, 1],
               max_leaf_nodes = [None, 20],
        )

        # Make a cartesian product of all options
        product = itertools.product(*options.values())
        args = [dict(zip(options.keys(), p)) for p in product]

        print("Testing a total of %s cases. This could take a while" % len(args))
        for it, arg in enumerate(args):
            metrics = self._train_convert_evaluate(**arg)
            self._check_metrics(metrics, arg)

@unittest.skipIf(not HAS_SKLEARN, 'Missing sklearn. Skipping tests.')
class BoostedTreeMultiClassClassificationBostonHousingScikitNumericTest(
           BoostedTreeClassificationBostonHousingScikitNumericTest):

    @classmethod
    def setUpClass(self):
        from sklearn.datasets import load_boston

        # Load data and train model
        import numpy as np
        scikit_data = load_boston()
        num_classes = 3
        self.X = scikit_data.data.astype('f').astype('d') ## scikit-learn downcasts data
        t = scikit_data.target
        target = np.digitize(t, np.histogram(t, bins = num_classes - 1)[1]) - 1

        # Save the data and the model
        self.scikit_data = scikit_data
        self.target = target
        self.feature_names = scikit_data.feature_names
        self.output_name = 'target'
        
    def test_simple_multiclass(self):
        metrics = self._train_convert_evaluate()
        self._check_metrics(metrics)
    
    @attr('slow')
    def test_multiclass_stress_test(self):
        options = dict(
               max_depth = [1, 10, None],
               min_samples_split = [2, 0.5],
               min_samples_leaf = [1, 5],
               min_weight_fraction_leaf = [0.0, 0.5],
               max_features = [None, 1],
               max_leaf_nodes = [None, 20],
        )

        # Make a cartesian product of all options
        product = itertools.product(*options.values())
        args = [dict(zip(options.keys(), p)) for p in product]

        print("Testing a total of %s cases. This could take a while" % len(args))
        for it, arg in enumerate(args):
            metrics = self._train_convert_evaluate(**arg)
            self._check_metrics(metrics, arg)
