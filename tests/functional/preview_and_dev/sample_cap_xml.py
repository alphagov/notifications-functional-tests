ALERT_XML = """
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>{identifier}</identifier>
        <sender>www.gov.uk/environment-agency</sender>
        <sent>{alert_sent}</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <scope>Public</scope>
        <info>
            <language>en-GB</language>
            <category>Met</category>
            <event>{event}</event>
            <urgency>Immediate</urgency>
            <severity>Severe</severity>
            <certainty>Likely</certainty>
            <expires>2022-06-15T12:12:13-00:00</expires>
            <senderName>Environment Agency</senderName>
            <description>{broadcast_content}</description>
            <instruction>Check the latest information for your area. </instruction>
            <area>
                <areaDesc>River Steeping</areaDesc>
                <polygon>53.10569,0.24453 53.10593,0.24430 53.10601,0.24375 53.10615,0.24349 53.10629,0.24356 53.10656,0.24336 53.10697,0.24354 53.10684,0.24298 53.10694,0.24264 53.10721,0.24302 53.10752,0.24310 53.10777,0.24308 53.10805,0.24320 53.10803,0.24187 53.10776,0.24085 53.10774,0.24062 53.10702,0.24056 53.10679,0.24088 53.10658,0.24071 53.10651,0.24049 53.10656,0.24022 53.10642,0.24022 53.10632,0.24052 53.10629,0.24082 53.10612,0.24093 53.10583,0.24133 53.10564,0.24178 53.10541,0.24282 53.10569,0.24453</polygon>
                <geocode>
                    <valueName>TargetAreaCode</valueName>
                    <value>053FWFSTEEP4</value>
                </geocode>
            </area>
        </info>
    </alert>
"""

CANCEL_XML = """
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>{identifier}</identifier>
        <sender>www.gov.uk/environment-agency</sender>
        <sent>{cancel_sent}</sent>
        <status>Actual</status>
        <msgType>Cancel</msgType>
        <scope>Public</scope>
        <references>www.gov.uk/environment-agency,{identifier},{alert_sent}</references>
        <info>
            <language>en-GB</language>
            <category>Met</category>
            <event>{event}</event>
            <urgency>Immediate</urgency>
            <severity>Severe</severity>
            <certainty>Likely</certainty>
            <expires>2022-06-15T12:12:13-00:00</expires>
            <senderName>Environment Agency</senderName>
            <description></description>
            <area>
                <areaDesc>River Steeping</areaDesc>
                <polygon>53.10569,0.24453 53.10593,0.24430 53.10601,0.24375 53.10615,0.24349 53.10629,0.24356 53.10656,0.24336 53.10697,0.24354 53.10684,0.24298 53.10694,0.24264 53.10721,0.24302 53.10752,0.24310 53.10777,0.24308 53.10805,0.24320 53.10803,0.24187 53.10776,0.24085 53.10774,0.24062 53.10702,0.24056 53.10679,0.24088 53.10658,0.24071 53.10651,0.24049 53.10656,0.24022 53.10642,0.24022 53.10632,0.24052 53.10629,0.24082 53.10612,0.24093 53.10583,0.24133 53.10564,0.24178 53.10541,0.24282 53.10569,0.24453</polygon>
                <geocode>
                    <valueName>TargetAreaCode</valueName>
                    <value>053FWFSTEEP4</value>
                </geocode>
            </area>
        </info>
    </alert>
"""
