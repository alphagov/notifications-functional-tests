The scripts in this directory are used to populate prod like environments in the following fashion:

- `cat $CSV_DOWNLOADED_FROM_BT | python process_sender_names.py`  - emits an insert statement that has a list of senderids to populate a table that lists those that are protected from being set. Admin will also raise a zendesk ticket if someone tries to set their senderid to one of those protected. It filters out all government and healthcare sender ids as we want those to be able to be set by our users. 


