import "../application"
import "../basiccontrols"
import "../coincontrols"

// TODO show result in BAddressEditBox.Type.*View
BDialog {
    property alias coin: _box.coin
    property alias type: _box.type

    property alias addressNameText: _box.addressNameText
    property alias labelText: _box.labelText
    property alias commentText: _box.commentText
    property alias isSegwit: _box.isSegwit

    title: _box.dialogTitleText
    contentItem: BAddressEditBox {
        id: _box
        onAddressNameTextChanged: {
            if (type === BAddressEditBox.Type.AddWatchOnly) {
                // TODO show invalid address message
                _acceptButton.enabled = BBackend.coinManager.isValidAddress(
                            coin.shortName,
                            addressNameText)
            }
        }
    }
    footer: BDialogButtonBox {
        BButton {
            id: _acceptButton
            BDialogButtonBox.buttonRole: BDialogButtonBox.AcceptRole
            text: _box.acceptText
            enabled: _box.type !== BAddressEditBox.Type.AddWatchOnly
        }
        BButton {
            BDialogButtonBox.buttonRole: BDialogButtonBox.RejectRole
            text: BCommon.button.cancelRole
        }
        BButton {
            BDialogButtonBox.buttonRole: BDialogButtonBox.ResetRole
            text: BCommon.button.resetRole
        }
    }

    onAboutToShow: {
        _box.forceActiveFocus()
    }
    onReset: {
        _box.clear()
    }
}
