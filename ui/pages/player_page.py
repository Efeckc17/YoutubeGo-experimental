from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSlider
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt

def create_player_page(main_window):
    page=QWidget()
    layout=QVBoxLayout(page)
    label=QLabel(main_window._("Video Player"))
    layout.addWidget(label)
    main_window.media_player=QMediaPlayer(None,QMediaPlayer.VideoSurface)
    main_window.video_widget=QVideoWidget()
    layout.addWidget(main_window.video_widget)
    main_window.media_player.setVideoOutput(main_window.video_widget)
    control_layout=QHBoxLayout()
    play_button=QPushButton(main_window._("Play"))
    play_button.clicked.connect(main_window.media_player.play)
    pause_button=QPushButton(main_window._("Pause"))
    pause_button.clicked.connect(main_window.media_player.pause)
    stop_button=QPushButton(main_window._("Stop"))
    stop_button.clicked.connect(main_window.media_player.stop)
    open_file_button=QPushButton(main_window._("Open File"))
    open_file_button.clicked.connect(main_window.open_video_file)
    main_window.position_slider=QSlider(Qt.Horizontal)
    main_window.position_slider.setRange(0,0)
    main_window.time_label=QLabel("00:00/00:00")
    main_window.playback_speed_slider=QSlider(Qt.Horizontal)
    main_window.playback_speed_slider.setRange(50,200)
    main_window.playback_speed_slider.setValue(100)
    main_window.playback_speed_label=QLabel("1.00x")
    main_window.volume_slider=QSlider(Qt.Horizontal)
    main_window.volume_slider.setRange(0,100)
    main_window.volume_slider.setValue(50)
    main_window.volume_label=QLabel("50%")
    main_window.media_player.positionChanged.connect(main_window.update_position)
    main_window.media_player.durationChanged.connect(main_window.update_duration)
    main_window.position_slider.sliderMoved.connect(main_window.set_position)
    main_window.playback_speed_slider.valueChanged.connect(main_window.change_playback_speed)
    main_window.volume_slider.valueChanged.connect(main_window.change_volume)
    for w in [play_button,pause_button,stop_button,open_file_button,main_window.position_slider,main_window.time_label,main_window.playback_speed_label,main_window.playback_speed_slider,main_window.volume_label,main_window.volume_slider]:
        control_layout.addWidget(w)
    layout.addLayout(control_layout)
    layout.addStretch()
    return page
