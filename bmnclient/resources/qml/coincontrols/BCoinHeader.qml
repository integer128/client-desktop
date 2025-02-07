import "../basiccontrols"

BControl {
    id: _base
    property var coin // CoinModel
    property BMenu contextMenu

    padding: _applicationStyle.padding
    contentItem: BRowLayout {
        BIconLabel {
            BLayout.fillWidth: true
            icon.width: _applicationStyle.icon.largeWidth
            icon.height: _applicationStyle.icon.largeHeight
            icon.source: _applicationManager.imagePath(_base.coin.iconPath)
            font.bold: true
            font.pointSize: _base.font.pointSize * _applicationStyle.fontPointSizeFactor.huge
            text: _base.coin.fullName
        }
        BAmountLabel {
            amount: _base.coin.amount
        }
        BContextMenuToolButton {
            font.pointSize: _base.font.pointSize * _applicationStyle.fontPointSizeFactor.huge
            menu: _base.contextMenu
        }
    }
}
