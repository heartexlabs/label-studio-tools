from label_studio_tools.core.label_config import parse_config, is_video_object_tracking


def test_parsing_label_config():
    """
    Test frames extraction with disabled in the end and frame count > disabled key frame
    """
    label_config = '''
            <View><Text name="meta_info" value="$meta_info"></Text>
              <Text name="text" value=" $text "></Text>
              <Choices name="text_class" choice="single" toName="text">
                <Choice value="class_A"></Choice>
                <Choice value="class_B"></Choice>
              </Choices>
            </View>'''
    config = parse_config(label_config)
    assert 'text_class' in config
    assert config['text_class']['type'] == 'Choices'
    assert config['text_class']['to_name'] == ['text']
    assert config['text_class']['labels'] == ['class_A', 'class_B']


def test_is_video_object_tracking():
    """
    Test is_video_object_tracking for video config
    """
    label_config = parse_config('''
                <View>
              <Labels name="videoLabels" toName="video">
                <Label value="Car"/>
                <Label value="Person"/>
              </Labels>
              <Video name="video" value="$video"/>
              <VideoRectangle name="box" toName="video"/>
            </View>''')
    assert is_video_object_tracking(label_config)


def test_is_video_object_tracking_not_video():
    """
    Test is_video_object_tracking for Audio config
    """
    label_config = parse_config('''
                <View>
                  <Header value="Listen to the audio"/>
                  <Audio name="audio" value="$audio"/>
                  <Header value="Select its topic"/>
                  <Choices name="topic" toName="audio"
                           choice="single-radio" showInline="true">
                    <Choice value="Politics"/>
                    <Choice value="Business"/>
                    <Choice value="Education"/>
                    <Choice value="Other"/>
                  </Choices>
                </View>''')
    assert not is_video_object_tracking(label_config)


def test_label_config_with_valueType_url():
    """
    Test config with value type = url
    """
    label_config = '''
            <View><Text name="meta_info" value="$meta_info"></Text>
              <Text name="text" value="$text" valueType="url"></Text>
              <Choices name="text_class" choice="single" toName="text">
                <Choice value="class_A"></Choice>
                <Choice value="class_B"></Choice>
              </Choices>
            </View>'''
    config = parse_config(label_config)
    assert config['text_class']['inputs'][0]['valueType'] == 'url'