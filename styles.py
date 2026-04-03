HOJA_ESTILOS = """
QMainWindow {
    background-color: #0c0c18;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Manrope', sans-serif;
}

QWidget {
    background-color: #0c0c18;
    color: #e2e8f0;
}

QTabWidget::pane {
    border: 1px solid #1a1a30;
    background-color: #0c0c18;
}

QTabBar::tab {
    background-color: #0f0f1c;
    color: #a0a0b0;
    padding: 12px 24px;
    margin-right: 5px;
    border: none;
    border-bottom: 3px solid transparent;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

QTabBar::tab:hover {
    color: #00D9FF;
    border-bottom-color: rgba(0, 217, 255, 0.3);
    background-color: rgba(0, 217, 255, 0.05);
}

QTabBar::tab:selected {
    color: #00D9FF;
    border-bottom-color: #8B2BE2;
    background-color: rgba(139, 43, 226, 0.1);
}

QLabel {
    color: #e2e8f0;
    background-color: transparent;
}

#pageTitle {
    font-size: 42px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0px;
    margin-bottom: 5px;
}

#pageSubtitle {
    font-size: 11px;
    color: #a0a0b0;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 30px;
}

#songTitle {
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
}

#songArtist {
    font-size: 16px;
    font-weight: 600;
    color: #00D9FF;
}

#nextSongLabel {
    font-size: 11px;
    color: #7a7a8a;
    font-style: italic;
}

#statusLabel {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}

#statusLabel[playing="true"] {
    color: #34d399;
}

#statusLabel[playing="false"] {
    color: #fbbf24;
}

#miniTitle {
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
}

#miniArtist {
    font-size: 11px;
    color: #00D9FF;
    font-weight: 600;
}

#libraryStatsLabel {
    font-size: 12px;
    color: #a0a0b0;
    margin-top: 3px;
    font-style: italic;
}

#statCard {
    background-color: #16162a;
    border: 1px solid #8B2BE2;
    border-top: 4px solid #00D9FF;
    border-radius: 12px;
    padding: 20px;
}

#statCard:hover {
    background-color: #1c1c35;
    border-color: #00D9FF;
}

#statNumber {
    font-size: 38px;
    font-weight: 800;
    color: #ffffff;
    margin: 10px 0;
}

#statLabel {
    font-size: 11px;
    color: #00D9FF;
    text-transform: uppercase;
    font-weight: 700;#favBtn {
    background: transparent;
    color: #e2e8f0;
    font-size: 20px;
    padding: 0;
    border: none;
}

#favBtn:hover {
    color: #00D9FF;
}

#favBtn[fav="true"] {
    color: #ff0000;
}

#delBtn {
    background: transparent;
    color: #ff4d4d;
    font-size: 16px;
    padding: 0;
    border: none;
}

#delBtn:hover {
    color: #ff8080;
}
    letter-spacing: 1.5px;
}

#statIcon {
    font-size: 24px;
    color: #FF006E;
}

#statBar {
    height: 3px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B2BE2, stop:1 #00D9FF);
    border-radius: 2px;
    margin-top: 15px;
}

.statCard {
    background: rgba(26, 26, 46, 0.8);
    border: 1px solid rgba(139, 43, 226, 0.3);
    border-radius: 10px;
    padding: 12px;
    min-width: 151px;
}

.statIcon {
    font-size: 18px;
}

.statNumber {
    color: #ffffff;
    font-size: 22px;
    font-weight: 800;
}

.statLabel {
    color: #00D9FF;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.statDecor {
    height: 4px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B2BE2, stop:1 #00D9FF);
    border-radius: 2px;
}
QPushButton {
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

#primaryBtn {
    background: #8B2BE2;
    color: #ffffff;
}

#primaryBtn:hover {
    background: #A040FF;
}

#secondaryBtn {
    background-color: #1c1c35;
    color: #ffffff;
    border: 1px solid #8B2BE2;
}

#secondaryBtn:hover {
    background-color: #252545;
}

#controlBtn {
    background-color: #ffffff;
    color: #0d0d1e;
    border: 1px solid transparent;
    border-radius: 20px;
    width: 40px;
    height: 40px;
    padding: 0;
    font-size: 18px;
    font-weight: bold;
}

#controlBtn:hover {
    background-color: #f0f0f0;
    border: 1px solid #00D9FF;
}

#controlBtn[active="true"] {
    background-color: #00D9FF;
    color: #0d0d1e;
    border: 1px solid #ffffff;
}

#playBtn {
    background-color: #ffffff;
    color: #0d0d1e;
    border: none;
    border-radius: 35px;
    width: 70px;
    height: 70px;
    padding: 0;
    font-size: 26px;
}

#playBtn:hover {
    background-color: #00D9FF;
}



#bottomBar {
    background-color: #0a0a1a;
    border-top: 2px solid #8B2BE2;
    padding: 15px;
}

QLineEdit {
    background-color: rgba(30, 30, 45, 0.6);
    color: #e2e8f0;
    border: 1px solid rgba(139, 43, 226, 0.3);
    border-radius: 4px;
    padding: 8px 12px;
}

QSlider::groove:horizontal {
    background: rgba(139, 43, 226, 0.2);
    height: 6px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #8B2BE2;
    width: 18px;
    height: 18px;
    margin: -6px 0px;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8B2BE2, stop:1 #00D9FF);
    border-radius: 3px;
}

QTableWidget {
    background-color: #0f0f1c;
    alternate-background-color: #0a0a15;
    gridline-color: #1a1a30;
    border: 1px solid rgba(139, 43, 226, 0.2);
    color: #ffffff;
}

QTableWidget::item {
    padding: 5px;
}

QTableWidget::item:selected {
    background-color: rgba(139, 43, 226, 0.3);
    color: #00D9FF;
}

QHeaderView::section {
    background: rgba(139, 43, 226, 0.2);
    color: #00D9FF;
    padding: 8px;
    border: none;
    font-weight: 700;
}

QScrollBar:vertical {
    background-color: #0c0c18;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: rgba(139, 43, 226, 0.5);
    border-radius: 5px;
}

QMenu {
    background-color: #0f0f1c;
    border: 1px solid rgba(139, 43, 226, 0.3);
    color: #e2e8f0;
}

QMenu::item:selected {
    background-color: #8B2BE2;
    color: #ffffff;
}
"""
