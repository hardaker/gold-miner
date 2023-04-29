The following report describes the test and evaluation of the
following datasets:

Evaluation Parameter     Value
--------------------     -----------------------------
**Classifier algorithm** *lms*
**Training files**       6
**Test files**           6
**Processors used**      8
**Processing time**      0.0976 minutes
**Result AUC**           0.8444

# Result summary

## Summarized training results

Training analysis estimates the difference in fingerprinting the
various protocols in the chart below, where a lighter color (yellow)
represents greater diversity between the protocols and easier to
identify against the corresponding.

![](training-similarity.png)

## Summarized test evaluation results

Evaluation results, with blue indicating good (true-positives) and red
indicating false positive rates.  These results are likely more
accurate than the estimated similarity above.

![](comparison.png)

The ROC curve for these test results:

![](results-ROC.png)

## Measured Classifier Precisions

Classifier                                tp  fp Precision
---------------------------------------- --- --- ---------
email-client                               1   1 0.5000
email-server                               1   0 1.0000
https-client                               1   0 1.0000
https-server                               1   0 1.0000
ftp-client                                 1   0 1.0000

## Individual Classifier ROCs



### Classifier ROC: email-client

![](results-email-client-ROC.png)


### Classifier ROC: email-server

![](results-email-server-ROC.png)


### Classifier ROC: https-client

![](results-https-client-ROC.png)


### Classifier ROC: https-server

![](results-https-server-ROC.png)


### Classifier ROC: ftp-client

![](results-ftp-client-ROC.png)


# Detailed test results

The following section describes each test case and whether the
classification model successfully identified the traffic in question.
Each file below contains a graph showing the detection
pseudo-confidence between 0.0 and 1.0, along with the classifier
confidence scores per flow-identifier within the traffic observed.




## <img src="check.svg" class="result"/> Test 1: email-client traffic


* File: ipsec-data/email-smtp.pcap
    * Filtered applied: esp and src 10.0.3.2
    * Packets processed: 1400
* Traffic label: email-client

* Processing time: 0.0107 minutes


![](b1f1fc5a469f926f506c1a1520b0f613f4ac2df146f4fba7b4e365bbbece6d15.test.0.png)

### Flows identified:



- <img src="check.svg" class="result"/> flow identifier: (50, '10.0.3.2', '10.0.6.2')
    - Total packets: 1400


    Label                                    Score
    ---------------------------------------- --------
    email-client                             0.7169
    https-server                             0.3331
    email-server                             0.2185
    ftp-server                               0.1667
    https-client                             0.0934
    ftp-client                               0.0613





## <img src="check.svg" class="result"/> Test 2: email-server traffic


* File: ipsec-data/email-smtp.pcap
    * Filtered applied: esp and src 10.0.6.2
    * Packets processed: 1400
* Traffic label: email-server

* Processing time: 0.0087 minutes


![](2b132ea16444177e7f574e554b49bfb52d14f159ed1e518d64279002dd719b8f.test.1.png)

### Flows identified:



- <img src="check.svg" class="result"/> flow identifier: (50, '10.0.6.2', '10.0.3.2')
    - Total packets: 1400


    Label                                    Score
    ---------------------------------------- --------
    email-server                             0.9857
    ftp-server                               0.5000
    https-client                             0.3361
    email-client                             0.1573
    https-server                             0.1537
    ftp-client                               0.1205





## <img src="check.svg" class="result"/> Test 3: https-client traffic


* File: ipsec-data/web-browsing.pcap
    * Filtered applied: esp and src 10.0.3.2
    * Packets processed: 1400
* Traffic label: https-client

* Processing time: 0.0079 minutes


![](7b0e1b4ef729ffec4f544e803ed07b23170c1615694f5063f3030c361355481c.test.2.png)

### Flows identified:



- <img src="check.svg" class="result"/> flow identifier: (50, '10.0.3.2', '10.0.6.2')
    - Total packets: 1400


    Label                                    Score
    ---------------------------------------- --------
    https-client                             0.9286
    email-server                             0.3898
    ftp-server                               0.2222
    https-server                             0.1537
    email-client                             0.0976
    ftp-client                               0.0243





## <img src="check.svg" class="result"/> Test 4: https-server traffic


* File: ipsec-data/web-browsing.pcap
    * Filtered applied: esp and src 10.0.6.2
    * Packets processed: 1400
* Traffic label: https-server

* Processing time: 0.0120 minutes


![](c7ed7c5e4b1278f401f101efd7cb9d349fb255440806ffab6abb7047eb699bfc.test.3.png)

### Flows identified:



- <img src="check.svg" class="result"/> flow identifier: (50, '10.0.6.2', '10.0.3.2')
    - Total packets: 1400


    Label                                    Score
    ---------------------------------------- --------
    https-server                             0.9806
    email-client                             0.3772
    ftp-server                               0.1542
    email-server                             0.1493
    https-client                             0.1293
    ftp-client                               0.0469





## <img src="check.svg" class="result"/> Test 5: ftp-client traffic


* File: ipsec-data/ftp.pcap
    * Filtered applied: esp and src 10.0.3.2
    * Packets processed: 1400
* Traffic label: ftp-client

* Processing time: 0.0038 minutes


![](9ed41639cc18bc7484c0bec6740b82fdd4a28ef438e6a511970ca802da134d21.test.4.png)

### Flows identified:



- <img src="check.svg" class="result"/> flow identifier: (50, '10.0.3.2', '10.0.6.2')
    - Total packets: 1400


    Label                                    Score
    ---------------------------------------- --------
    ftp-client                               0.4018
    ftp-server                               0.2857
    email-server                             0.1954
    https-client                             0.0407
    https-server                             0.0383
    email-client                             0.0380





## <img src="cancel.svg" class="result"/> Test 6: ftp-server traffic


* File: ipsec-data/ftp.pcap
    * Filtered applied: esp and src 10.0.6.2
    * Packets processed: 1400
* Traffic label: ftp-server

* Processing time: 0.0043 minutes


![](ee7ce0f19c30f6f67a701fd48f620fbe30eb65ee24bc7a0d2c891fabc6adcafd.test.5.png)

### Flows identified:



- <img src="cancel.svg" class="result"/> flow identifier: (50, '10.0.6.2', '10.0.3.2')
    - Total packets: 1400


    Label                                    Score
    ---------------------------------------- --------
    email-client                             0.0200
    https-server                             0.0195
    ftp-server                               0.0012
    email-server                             0.0000
    https-client                             0.0000
    ftp-client                               0.0000
