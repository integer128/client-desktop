import QtQuick 2.12
import "../widgets"
import "../controls"
import "../api"
import "../js/functions.js" as Funcs
import "../js/constants.js" as Constants



BasePage {
    id: _base

    readonly property int pageId: Constants.pageId.main

    function home(){
        _base.state = "coin_list";
    }

    function newAddress(coinIndex){
        var coin = api.coinModel[coinIndex]
        if(coin){
            _make_address.coinName = coin.fullName
            _make_address.coinIndex = coinIndex
            _make_address.label = ""
            _make_address.open()
        }
    }

    function addWatchOnlyAddress(coinIndex){
        var coin = api.coinModel[coinIndex]
        if(coin){
            _watch_address.coinName = coin.fullName
            _watch_address.coinIndex = coinIndex
            _watch_address.open()
        }
    }

    MakeAddressPopup{
        id: _make_address
        property int coinIndex: -1
        onMake: {
            api.makeAddress(coinIndex, label, segwit);
            close();
        }
    }

    AddWatchAddressPopup{
        id: _watch_address
        property int coinIndex: -1
        onAdd: {
            api.addWatchAddress( coinIndex , address, label )
            close()
        }
    }

    Row{
        anchors.fill: parent
        Item{
            id: _list_area
            width: parent.width * 0.5
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            CoinListPanel{
                id: _coin_list
                anchors.fill: parent
                model: CoinApi.coins.coinModel
                onCoinSelect:{
                    api.coinIndex = index
                }
                onAddressSelect: {
                    api.addressIndex = index
                }
                onCreateAddress: {
                    newAddress(index)
                }
                onAddWatchAddress: {
                    addWatchOnlyAddress(index)
                }
            }
        }


        Connections{
            function coin_handler(){
                        if( api.coin && api.coin.wallets.length > 0 ){
                            _base.state = "address_list"
                            // doesn't change
                            _address_info.unit = api.coin.unit
                            _address_info.coinName = api.coin.fullName;
                            _address_info.fiatUnit = api.currency
                        }else{
                            _base.state = "coin_list"
                            _coin_list.closeList()
                        }
            }
            target: api
            onAddressIndexChanged:{
                    if( api.address ){
                        _address_info.coinName = api.coin.fullName
                        _address_info.coinIcon = Funcs.loadImage( api.coin.icon)
                        _address_info.amount =	CoinApi.settings.coinBalance(api.address.balance)
                        _address_info.fiatAmount = api.address.fiatBalance
                    }else{
                        _base.state = "coin_list"
                        _coin_list.closeList()
                    }
                    console.log(`new address ${api.address} state:${state}`)
            }
            onCoinIndexChanged:{
                    coin_handler();
                    console.log(`new coin ${api.coin} state:${state}`)
                }
            onAddressModelChanged:{
                coin_handler();
                    console.log(`new add model`)
                }
        }


        Rectangle{

            id: _info_area
            width: parent.width * 0.5
            x: width
            color: palette.window
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            /*
            gradient: LinearBg{
                colorOne: palette.base
                colorTwo: palette.mid
            }
            */

            SelectCoin {
                id: _no_selection_info
                anchors.fill: parent
            }

            AddressInfoPanel{
                id: _address_info
                anchors.fill: parent
                readOnly: api.address === null || api.address.readOnly

                function do_tx(page ){
                    let settings= {
                        "coinName": _address_info.coinName,
                        "coinIcon": _address_info.coinIcon,
                    }
                    pushPage(page,settings);
                }
                onSendMoney: do_tx("SendPage.qml")
                onReceiveMoney: do_tx("ReceivePage.qml")
                onExchangeMoney: {
                    pushPage("ExchangePage.qml")
                }
            }
        }
    }



    /*
        state stuff
    */
    state: "coin_list"
    states: [
        State {
            name: "coin_list"
            PropertyChanges {
                target: _address_info
                visible: false
                coinName: ""
                coinIcon: ""
                amount: ""
                fiatAmount: ""
                isUpdating: false
            }
            PropertyChanges {
                target: _no_selection_info
                visible: true
            }
        },
        State {
            name: "address_list"
            PropertyChanges {

                target: _address_info
                visible: true
                coinName: api.coin.fullName
                coinIcon: api.coin? Funcs.loadImage( api.coin.icon ):""
                readOnly: !api.address || api.address.readOnly 
                receiveOnly: api.address.balance == 0.
                amount: api.address? api.address.balanceHuman : ""
                fiatAmount: api.address? api.address.fiatBalance : ""
                isUpdating: api.address? api.address.isUpdating : false
            }
            PropertyChanges {
                target: _no_selection_info
                visible: false
            }
        }
    ]

}
