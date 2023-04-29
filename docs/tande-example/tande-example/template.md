The following report describes the test and evaluation of the
following datasets:

Evaluation Parameter     Value
--------------------     -----------------------------
**Classifier algorithm** *{{algorithm_used}}*
**Training files**       {{training_results | length}}
**Test files**           {{test_results | length}}
**Processors used**      {{processes}}
**Processing time**      {{tande_time}} minutes
**Result AUC**           {{test_auc}}

# Result summary

## Summarized training results

Training analysis estimates the difference in fingerprinting the
various protocols in the chart below, where a lighter color (yellow)
represents greater diversity between the protocols and easier to
identify against the corresponding.

![]({{similarities}})

## Summarized test evaluation results

Evaluation results, with blue indicating good (true-positives) and red
indicating false positive rates.  These results are likely more
accurate than the estimated similarity above.

![](comparison.png)

The ROC curve for these test results:

![](results-ROC.png)

## Measured Classifier Precisions

{{"%-40s" | format("Classifier")}}  tp  fp Precision
---------------------------------------- --- --- ---------
{%- for key in bytype_results %}
{{"%-40s" | format(key)}} {{"%3d" | format(bytype_results[key]['good'])}} {{"%3d" | format(bytype_results[key]['bad'])}} {{"%0.4f" | format(bytype_results[key]['percent'])}}
{%- endfor %}

## Individual Classifier ROCs

{% for classifier in bytype_results %}

### Classifier ROC: {{classifier}}

![](results-{{classifier}}-ROC.png)
{% endfor %}

# Detailed test results

The following section describes each test case and whether the
classification model successfully identified the traffic in question.
Each file below contains a graph showing the detection
pseudo-confidence between 0.0 and 1.0, along with the classifier
confidence scores per flow-identifier within the traffic observed.

{% for file in test_results %}

{% if file['all_true'] %}
## <img src="check.svg" class="result"/> Test {{loop.index}}: {{file['label']}} traffic
{% else %}
## <img src="cancel.svg" class="result"/> Test {{loop.index}}: {{file['label']}} traffic
{% endif %}

* File: {{file['file']}}
{% if file['test_specification']['filter_applied'] %}    * Filtered applied: {{file['test_specification']['filter_applied']}} {% endif %}
    * Packets processed: {{file['total_count']}}
* Traffic label: {{file['label']}}
{% if file['mapped_label'] != file['label'] %}    * Remapped label: {{file['mapped_label']}}{% endif %}
* Processing time: {{file['processing_time']}} minutes


![]({{file['graph']}})

### Flows identified:

{% for identifier in file['results'] %}
{% set keys = file['results'][identifier] | dictsort(false, 'value', reverse=True)  %}
- {% if keys[0][0] == file['label'] %}<img src="check.svg" class="result"/>{% else %}<img src="cancel.svg" class="result"/>{% endif %} flow identifier: {{identifier}}
    - Total packets: {{file['identifier_counts'][identifier]}}

    {% set mydict = file['results'][identifier] %}
    {{"%-40s" | format("Label")}} Score
    {{"%-40s" | format("----------------------------------------")}} --------
    {%- for label, value in mydict | dictsort(false, 'value', reverse=True) %}
    {{"%-40s" | format(label)}} {{"%0.4f" | format(value)}}
    {%- endfor %}
{% endfor %}

{% endfor %}
