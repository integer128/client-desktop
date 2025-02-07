import "../application"
import "../basiccontrols"

BPane {
    property string title: qsTr("Application")
    property string iconPath: _applicationManager.imagePath("icon-info.svg")

    contentItem: BDialogScrollableLayout {
        BLogoImage {
            BLayout.columnSpan: parent.columns
            BLayout.minimumWidth: implicitWidth
            BLayout.alignment: Qt.AlignTop | Qt.AlignHCenter
            huge: true
        }

        BDialogSeparator {
            BLayout.minimumWidth: _applicationStyle.dialogInputWidth
            transparent: true
        }

        BInfoLayout {
            BLayout.columnSpan: parent.columns
            BLayout.fillWidth: true

            BInfoLabel {
                text: qsTr("Application name:")
            }
            BInfoValue {
                text: Qt.application.name
            }
            BInfoSeparator {}

            BInfoLabel {
                text: qsTr("Application version:")
            }
            BInfoValue {
                text: Qt.application.version
            }
            BInfoSeparator {}
        }

        BDialogSpacer {}
        BLabel {
            BLayout.columnSpan: parent.columns
            BLayout.minimumWidth: implicitWidth
            BLayout.alignment: Qt.AlignBottom | Qt.AlignHCenter

            font.bold: true
            // TODO year from compile time
            text: qsTr("Copyright © 2020-2021 %1.\nAll rights reserved.").arg(Qt.application.organization)
            horizontalAlignment: BLabel.AlignHCenter
        }
    }
}
