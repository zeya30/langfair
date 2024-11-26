# Copyright 2024 CVS Health and/or one of its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from numpy.typing import ArrayLike

from langfair.metrics.classification.metrics.baseclass.metrics import Metric


class FalseNegativeRateParity(Metric):
    def __init__(self) -> None:
        """
        This class computes false negative rate parity. The user may specify whether to compute this
        metric as a difference or a ratio. For more information on these metrics,
        see Bellamy et al. (2018) :footcite:`bellamy2018aifairness360extensible` and Saleiro et al. (2019) :footcite:`saleiro2019aequitasbiasfairnessaudit`.
        """
        self.name = "FalseNegativeRateParity"

    def evaluate(
        self,
        groups: ArrayLike,
        y_pred: ArrayLike,
        y_true: ArrayLike,
        ratio: bool = False,
    ) -> float:
        """
        This method computes disparity in false negative rates between two groups.

        Parameters
        ----------
        groups : Array-like
            Group indicators. Must contain exactly two unique values.

        y_pred : Array-like
            Binary model predictions. Positive and negative predictions must be 1 and 0, respectively.

        y_true : Array-like, default=None
            Binary labels (ground truth values). Positive and negative labels must be 1 and 0, respectively.

        ratio : bool, default=False
            Indicates whether to compute the metric as a difference or a ratio

        Returns
        -------
        float
            Value of false negative rate parity

        References
        ----------
        .. footbibliography::
        """
        unique_preds, unique_labels, unique_groups = (
            np.unique(y_pred),
            np.unique(y_true),
            np.unique(groups),
        )
        assert np.array_equal(
            unique_preds, [0, 1]
        ), "y_pred must contain exactly two unique values: 0 and 1"
        assert np.array_equal(
            unique_labels, [0, 1]
        ), "y_true must contain exactly two unique values: 0 and 1"
        assert len(unique_groups) == 2, "groups must contain exactly two unique values"

        cm1 = self.binary_confusion_matrix(
            y_true[groups == unique_groups[0]], y_pred[groups == unique_groups[0]]
        )

        cm2 = self.binary_confusion_matrix(
            y_true[groups == unique_groups[1]], y_pred[groups == unique_groups[1]]
        )

        fnr1 = (
            cm1[1][0] / (cm1[1][0] + cm1[1][1])
            if (cm1[1][0] + cm1[1][1]) != 0
            else None
        )
        fnr2 = (
            cm2[1][0] / (cm2[1][0] + cm2[1][1])
            if (cm1[1][0] + cm1[1][1]) != 0
            else None
        )

        assert fnr1 and fnr2, """
        Unable to compute false negative rate for both groups. Please ensure that positive labels exist for both groups.
        """

        return fnr1 / fnr2 if ratio else abs(fnr1 - fnr2)
