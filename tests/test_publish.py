import os
from publish import FritzPublish

class Args():
    protocol = ""
    fritz_detection_rules = "rule1, rule2"
    rule_split = fritz_detection_rules.split(',')

class Logs():
    l = ""

    def info(self, str):
        self.l = str

def test_is_connected(mocker):
    mocker.patch.object(os, "exit", return_value=1)

    args = Args()
    publish = FritzPublish(args, None, None, None)

    mock_response = True
    # Patch the method
    mocker.patch.object(publish, "is_connected", return_value=mock_response)

    assert publish.is_connected() == True

def test_prepare_msgs_no_errors(mocker):
    mocker.patch.object(os, "exit", return_value=1)

    args = Args()
    publish = FritzPublish(args, Logs(), None, None)

    downtime = [("timex", "rule_1")]
    
    msgs = publish.prepare_msgs(downtime)
    
    # len == len(fritz_detection_rules)
    assert len(msgs) == 2

    index = 0
    for _, msg in msgs:
        print (msg)
        assert msg[0]["measurement"] ==  "fritzbox-monitor"
        assert msg[0]["tags"]["rule"] ==  args.rule_split[index] if index == 0 else msg[0]["tags"]["rule"] !=  args.rule_split[index] 
        assert msg[0]["fields"]["count"] == 0
        index += 1

def test_prepare_msgs_with_error(mocker):
    mocker.patch.object(os, "exit", return_value=1)

    args = Args()
    publish = FritzPublish(args, Logs(), None, None)

    downtime = [("timex", "rule1")]
    
    msgs = publish.prepare_msgs(downtime)
    
    # len == len(fritz_detection_rules)
    assert len(msgs) == 2

    index = 0
    for _, msg in msgs:
        print (msg)
        assert msg[0]["measurement"] ==  "fritzbox-monitor"
        if index == 0:
            assert msg[0]["tags"]["rule"] ==  args.rule_split[index] 
            assert msg[0]["fields"]["count"] == 1 
        else:
            assert msg[0]["tags"]["rule"] !=  args.rule_split[index] 
            assert msg[0]["fields"]["count"] == 0
        index += 1

def test_prepare_msgs_with_errors(mocker):
    mocker.patch.object(os, "exit", return_value=1)

    args = Args()
    publish = FritzPublish(args, Logs(), None, None)

    downtime = [("timex", "rule1"), ("timex", "rule1"), ("timex", " rule2")]
    
    msgs = publish.prepare_msgs(downtime)
    
    # len == len(fritz_detection_rules)
    assert len(msgs) == 2

    index = 0
    for _, msg in msgs:
        print (msg)
        assert msg[0]["measurement"] ==  "fritzbox-monitor"
        if index == 0:
            assert msg[0]["tags"]["rule"] ==  args.rule_split[index] 
            assert msg[0]["fields"]["count"] == 2 
        else:
            assert msg[0]["tags"]["rule"] !=  args.rule_split[index] 
            assert msg[0]["fields"]["count"] == 1
        index += 1