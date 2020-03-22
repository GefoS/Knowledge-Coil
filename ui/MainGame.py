# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainGame.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *

import resource_rc

class Ui_MainGame(object):
    def setupUi(self, MainGame):
        if MainGame.objectName():
            MainGame.setObjectName(u"MainGame")
        MainGame.resize(530, 600)
        self.actionRedo = QAction(MainGame)
        self.actionRedo.setObjectName(u"actionRedo")
        self.actionRedo.setCheckable(True)
        self.actionClear = QAction(MainGame)
        self.actionClear.setObjectName(u"actionClear")
        self.actionClear.setCheckable(True)
        self.actionSkip = QAction(MainGame)
        self.actionSkip.setObjectName(u"actionSkip")
        self.actionSkip.setCheckable(True)
        self.centralwidget = QWidget(MainGame)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ButRedo = QPushButton(self.centralwidget)
        self.ButRedo.setObjectName(u"ButRedo")
        self.ButRedo.setMinimumSize(QSize(100, 25))
        icon = QIcon()
        icon.addFile(u":/icons/plus.png", QSize(), QIcon.Normal, QIcon.Off)
        self.ButRedo.setIcon(icon)
        self.ButRedo.setIconSize(QSize(25, 25))

        self.horizontalLayout.addWidget(self.ButRedo)

        self.ButClear = QPushButton(self.centralwidget)
        self.ButClear.setObjectName(u"ButClear")
        self.ButClear.setMinimumSize(QSize(100, 25))
        self.ButClear.setIcon(icon)
        self.ButClear.setIconSize(QSize(25, 25))

        self.horizontalLayout.addWidget(self.ButClear)

        self.ButSkip = QPushButton(self.centralwidget)
        self.ButSkip.setObjectName(u"ButSkip")
        self.ButSkip.setMinimumSize(QSize(100, 25))
        self.ButSkip.setIcon(icon)
        self.ButSkip.setIconSize(QSize(25, 25))

        self.horizontalLayout.addWidget(self.ButSkip)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_2 = QSpacerItem(30, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.ImageHolder = QLabel(self.centralwidget)
        self.ImageHolder.setObjectName(u"ImageHolder")
        self.ImageHolder.setPixmap(QPixmap(u":/icons/test.png"))
        self.ImageHolder.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.ImageHolder)

        self.verticalSpacer = QSpacerItem(30, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.Log = QPlainTextEdit(self.centralwidget)
        self.Log.setObjectName(u"Log")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Log.sizePolicy().hasHeightForWidth())
        self.Log.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(14)
        self.Log.setFont(font)

        self.horizontalLayout_2.addWidget(self.Log)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.Timer = QLabel(self.centralwidget)
        self.Timer.setObjectName(u"Timer")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Timer.sizePolicy().hasHeightForWidth())
        self.Timer.setSizePolicy(sizePolicy1)
        self.Timer.setMinimumSize(QSize(200, 0))
        self.Timer.setMaximumSize(QSize(16777215, 16777215))
        font1 = QFont()
        font1.setFamily(u"Trebuchet MS")
        font1.setPointSize(48)
        font1.setBold(True)
        font1.setWeight(75)
        self.Timer.setFont(font1)

        self.verticalLayout_2.addWidget(self.Timer)

        self.verticalSpacer_3 = QSpacerItem(100, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)


        self.horizontalLayout_2.addLayout(self.verticalLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        MainGame.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainGame)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 530, 21))
        MainGame.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainGame)
        self.statusbar.setObjectName(u"statusbar")
        MainGame.setStatusBar(self.statusbar)

        self.retranslateUi(MainGame)

        QMetaObject.connectSlotsByName(MainGame)
    # setupUi

    def retranslateUi(self, MainGame):
        MainGame.setWindowTitle(QCoreApplication.translate("MainGame", u"MainWindow", None))
        self.actionRedo.setText(QCoreApplication.translate("MainGame", u"Redo", None))
#if QT_CONFIG(shortcut)
        self.actionRedo.setShortcut(QCoreApplication.translate("MainGame", u"Ctrl+Z", None))
#endif // QT_CONFIG(shortcut)
        self.actionClear.setText(QCoreApplication.translate("MainGame", u"Clear", None))
#if QT_CONFIG(shortcut)
        self.actionClear.setShortcut(QCoreApplication.translate("MainGame", u"Space", None))
#endif // QT_CONFIG(shortcut)
        self.actionSkip.setText(QCoreApplication.translate("MainGame", u"Skip", None))
#if QT_CONFIG(shortcut)
        self.actionSkip.setShortcut(QCoreApplication.translate("MainGame", u"Ctrl+Space", None))
#endif // QT_CONFIG(shortcut)
        self.ButRedo.setText(QCoreApplication.translate("MainGame", u"\u041d\u0430\u0437\u0430\u0434", None))
        self.ButClear.setText(QCoreApplication.translate("MainGame", u"\u0417\u0430\u043d\u043e\u0432\u043e", None))
        self.ButSkip.setText(QCoreApplication.translate("MainGame", u"\u041f\u0440\u043e\u043f\u0443\u0441\u0442\u0438\u0442\u044c", None))
        self.ImageHolder.setText("")
        self.Log.setPlainText(QCoreApplication.translate("MainGame", u"A\n"
"B\n"
"C\n"
"D", None))
        self.Timer.setText(QCoreApplication.translate("MainGame", u"00:00", None))
    # retranslateUi

