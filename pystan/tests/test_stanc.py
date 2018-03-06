import unittest
import os

from pystan import stanc, StanModel
from pystan._compat import PY2


class TestStanc(unittest.TestCase):

    def test_stanc(self):
        model_code = 'parameters {real y;} model {y ~ normal(0,1);}'
        result = stanc(model_code=model_code)
        desired = sorted({"status", "model_cppname", "cppcode", "model_name", "model_code", "include_paths"})
        self.assertEqual(sorted(result.keys()), desired)
        self.assertTrue(result['cppcode'].startswith("// Code generated by Stan "))
        self.assertEqual(result['status'], 0)

    def test_stanc_exception(self):
        model_code = 'parameters {real z;} model {z ~ no_such_distribution();}'
        assertRaisesRegex = self.assertRaisesRegexp if PY2 else self.assertRaisesRegex
        # distribution not found error
        with assertRaisesRegex(ValueError, r'Probability function must end in _lpdf or _lpmf\. Found'):
            stanc(model_code=model_code)
        with assertRaisesRegex(ValueError, r'Probability function must end in _lpdf or _lpmf\. Found'):
            StanModel(model_code=model_code)

    def test_stanc_exception_semicolon(self):
        model_code = """
        parameters {
            real z
            real y
        }
        model {
            z ~ normal(0, 1);
            y ~ normal(0, 1);}
        """
        assertRaisesRegex = self.assertRaisesRegexp if PY2 else self.assertRaisesRegex
        with assertRaisesRegex(ValueError, 'Failed to parse'):
            stanc(model_code=model_code)
        with assertRaisesRegex(ValueError, 'Failed to parse'):
            StanModel(model_code=model_code)

    def test_stanc_include(self):
        model_code = 'parameters {\n#include external1.stan\n} model {\ny ~ normal(0,1);}'
        testdata_path = os.path.join(os.path.dirname(__file__), 'data', "")
        result = stanc(model_code=model_code, include_paths=[testdata_path])
        desired = sorted({"status", "model_cppname", "cppcode", "model_name", "model_code", "include_paths"})
        self.assertEqual(sorted(result.keys()), desired)
        self.assertEqual(result['status'], 0)

    def test_stanc_2_includes(self):
        model_code = 'parameters {\n#include external1.stan\n#include external2.stan\n} model {\ny ~ normal(0,1);\nz ~ normal(0,1)}'
        testdata_path = os.path.join(os.path.dirname(__file__), 'data', "")
        result = stanc(model_code=model_code, include_paths=[testdata_path])
        desired = sorted({"status", "model_cppname", "cppcode", "model_name", "model_code", "include_paths"})
        self.assertEqual(sorted(result.keys()), desired)
        self.assertEqual(result['status'], 0)
