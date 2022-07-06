COPY users (id, name, email_address, created_at, updated_at, _password, mobile_number, password_changed_at, logged_in_at, failed_login_count, state, platform_admin, current_session_id, auth_type, email_access_validated_at) FROM stdin;
44c41c45-0fb4-4ce8-8c92-72734e31995c	Functional Tests	notify-tests-preview+local@digital.cabinet-office.gov.uk	2019-03-25 14:48:38.719334	2019-03-25 14:50:58.826605	$2b$10$pQIWZpetCN4qCtGX0GdSou6D6CeNU97U2TLWL2DnucKjjncVTJcw.	07700900001	2019-03-25 14:48:38.71801	2019-03-25 14:50:58.796995	0	active	f	23ca4bbf-347f-44a7-b998-142bca2fa991	sms_auth	NOW()
0ebf8f7d-c511-498c-9762-41c4d47507ec	Functional Tests Email Auth	notify-tests-preview+local-email-auth@digital.cabinet-office.gov.uk	2019-03-25 15:12:53.939099	2019-03-25 15:45:48.148452	$2b$10$6k4SCUnF9q39Q/RasnGRXO0JaXoXRkd9x.vFLGG5Eo/8XOpgbdBQC	\N	2019-03-25 15:12:53.937723	2019-03-25 15:45:48.147457	0	active	f	a953c3c0-1edb-4852-a35e-1011bd1b6e20	email_auth	NOW()
c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	Preview admin tests user	notify-tests-preview+local-admin-tests@digital.cabinet-office.gov.uk	2019-03-25 15:00:54.012798	2021-07-14 14:54:06.524471	$2b$10$rX7KZQG7NvsyfwqNX/eZru6w79nDXsABV6uSqsckLcwIL9T8TfHlG	07700900501	2019-03-25 15:00:54.005881	2021-07-14 14:33:48.331781	0	active	f	\N	sms_auth	NOW()
0d2e9b87-9c54-448c-b549-f764231ee599	"Functional Tests - Broadcast User Create"	notify-tests-preview+local-broadcast1@digital.cabinet-office.gov.uk	2021-07-14 14:52:41.503215	2021-07-14 14:53:59.806529	$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC	07700900002	2021-07-14 14:52:41.496841	2021-07-14 14:53:00.204258	0	active	f	\N	sms_auth	NOW()
1048af40-45f6-4249-a670-df72ba3352d7	Functional Tests - Broadcast User Approve	notify-tests-preview+local-broadcast2@digital.cabinet-office.gov.uk	2021-07-14 14:52:41.503215	2021-07-14 14:53:59.806529	$2b$10$t2gDo8ymix/7BcPHZVxdNOh8uN1kEf.9tuMAOxgV79YzTUDAC70ZC	07700900003	2021-07-14 14:52:41.496841	2021-07-14 14:53:00.204258	0	active	f	\N	sms_auth	NOW()
\.

COPY organisation (id, name, active, created_at, updated_at, email_branding_id, letter_branding_id, agreement_signed, agreement_signed_at, agreement_signed_by_id, agreement_signed_version, crown, organisation_type, request_to_go_live_notes, agreement_signed_on_behalf_of_email_address, agreement_signed_on_behalf_of_name, billing_contact_email_addresses, billing_contact_names, billing_reference, notes, purchase_order_number) FROM stdin;
e6e6ce48-f634-4ebf-af7b-c70fdf16cbd5	Functional Tests Org	t	2019-03-25 15:04:27.500149	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.

COPY services (id, name, created_at, updated_at, active, message_limit, restricted, email_from, created_by_id, version, research_mode, organisation_type, prefix_sms, crown, rate_limit, contact_link, consent_to_research, volume_email, volume_letter, volume_sms, count_as_live, go_live_at, go_live_user_id, organisation_id, notes, billing_contact_email_addresses, billing_contact_names, billing_reference, purchase_order_number) FROM stdin;
34b725f0-1f47-49bc-a9f5-aa2a84587c53	Functional Tests	2019-03-25 15:02:40.869192	2019-03-25 15:35:17.203589	t	250000	f	functional.tests	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	5	f	central	t	t	3000	e6e6ce48-f634-4ebf-af7b-c70fdf16cbd5	\N	\N	\N	\N	t	\N	\N	\N	\N	\N	\N	\N	\N
8e1d56fa-12a8-4d00-bed2-db47180bed0a	Functional Tests Broadcast Service	2021-07-14 14:36:03.423486	2021-07-14 14:37:35.234642	t	50	f	functional.tests.broadcast.service	0d2e9b87-9c54-448c-b549-f764231ee599	2	f	central	t	\N	3000	\N	\N	\N	\N	\N	f	2021-07-14 14:37:35.122431	\N	38e4bf69-93b0-445d-acee-53ea53fe02df	\N	\N	\N	\N	\N
\.

COPY annual_billing (id, service_id, financial_year_start, free_sms_fragment_limit, updated_at, created_at) FROM stdin;
59380e42-93dd-4586-8148-189da82e84b7	34b725f0-1f47-49bc-a9f5-aa2a84587c53	2018	250000	\N	2019-03-25 15:02:40.927107
f1cb31a3-8f1e-4361-8def-c5789db9a64e	8e1d56fa-12a8-4d00-bed2-db47180bed0a	2021	150000	\N	2021-07-14 14:36:03.465174
\.

COPY api_keys (id, name, secret, service_id, expiry_date, created_at, created_by_id, updated_at, version, key_type) FROM stdin;
ccadd239-bae1-4ade-9f5b-fc389a1622a9	govuk_notify	IjhmNjBiNDIzLTkwZmItNGQ0OC1hN2NiLTYyZTc1ODBjZDg4MSI.IRb1WKwUfeMS0AhcG9cUDkr5m50	d6aa2c68-a2d9-4437-ab19-3ae8eb202553	\N	2019-03-25 14:57:08.679353	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	\N	1	normal
c1d8e17f-3abe-4858-913e-d88f689ca430	functional_tests_service_live_key	Ijg0NmE4OTc1LTllMzctNDUzMC1iYTJiLTZlZDUzODE5Yjc4ZCI.S9_8a8r5rGLqvFhwC2AOXT1g3C4	34b725f0-1f47-49bc-a9f5-aa2a84587c53	\N	2019-03-25 15:07:17.182987	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	\N	1	normal
9e80ccb3-98fb-4b0b-84c0-40a9443e326b	functional_tests_service_test_key	ImZmYWYyZGVjLWU3ZGEtNGZiZS1iY2M3LWNlNmFkNTFlM2I1ZSI.hU8Q_AkTwYvlsdYyShU7H38Qw8U	34b725f0-1f47-49bc-a9f5-aa2a84587c53	\N	2019-03-25 15:07:44.583174	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	\N	1	test
22404b3f-779c-49d5-9c3f-46464fb37a62	func_tests_broadcast_service_live_key	ImMzZTZiNjhmLWJkNDMtNGUzMy04ZmJhLTY3YThjMWJhZDRhMyI.58oYXhsespJeQQ0zolZUdfyTnPw	8e1d56fa-12a8-4d00-bed2-db47180bed0a	\N	2019-03-25 15:07:44.583174	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	\N	1	normal
\.

COPY api_keys_history (id, name, secret, service_id, expiry_date, created_at, updated_at, created_by_id, version, key_type) FROM stdin;
ccadd239-bae1-4ade-9f5b-fc389a1622a9	govuk_notify	IjhmNjBiNDIzLTkwZmItNGQ0OC1hN2NiLTYyZTc1ODBjZDg4MSI.IRb1WKwUfeMS0AhcG9cUDkr5m50	d6aa2c68-a2d9-4437-ab19-3ae8eb202553	\N	2019-03-25 14:57:08.679353	\N	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	normal
c1d8e17f-3abe-4858-913e-d88f689ca430	functional_tests_service_live_key	Ijg0NmE4OTc1LTllMzctNDUzMC1iYTJiLTZlZDUzODE5Yjc4ZCI.S9_8a8r5rGLqvFhwC2AOXT1g3C4	34b725f0-1f47-49bc-a9f5-aa2a84587c53	\N	2019-03-25 15:07:17.182987	\N	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	normal
9e80ccb3-98fb-4b0b-84c0-40a9443e326b	functional_tests_service_test_key	ImZmYWYyZGVjLWU3ZGEtNGZiZS1iY2M3LWNlNmFkNTFlM2I1ZSI.hU8Q_AkTwYvlsdYyShU7H38Qw8U	34b725f0-1f47-49bc-a9f5-aa2a84587c53	\N	2019-03-25 15:07:44.583174	\N	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	test
22404b3f-779c-49d5-9c3f-46464fb37a62	func_tests_broadcast_service_live_key	ImMzZTZiNjhmLWJkNDMtNGUzMy04ZmJhLTY3YThjMWJhZDRhMyI.58oYXhsespJeQQ0zolZUdfyTnPw	8e1d56fa-12a8-4d00-bed2-db47180bed0a	\N	2019-03-25 15:07:44.583174	\N	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	normal
\.

COPY templates_history (id, name, template_type, created_at, updated_at, content, service_id, subject, created_by_id, version, archived, process_type, service_letter_contact_id, hidden, postage, broadcast_data) FROM stdin;
75a02fb0-177a-4d10-89f8-e28e48ede6e5	Functional Tests - CSV Email Template with Jenkins Build ID	email	2019-03-25 15:23:07.172674	\N	The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).	34b725f0-1f47-49bc-a9f5-aa2a84587c53	Functional Tests - CSV Email	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	f	normal	\N	f	\N	\N
63d41316-1c0a-415b-968b-8211a71ab7f1	Functional Tests - CSV SMS Template with Jenkins Build ID	sms	2019-03-25 15:24:14.907439	\N	The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).	34b725f0-1f47-49bc-a9f5-aa2a84587c53	\N	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	f	normal	\N	f	\N	\N
c3caccab-b066-4a43-8340-cae8b2887e86	Functional Tests - CSV Letter Template with Jenkins Build ID	letter	2019-03-25 15:24:40.689266	2019-03-25 15:26:51.614382	The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).	34b725f0-1f47-49bc-a9f5-aa2a84587c53	Functional Tests - CSV Letter	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	2	f	normal	\N	f	second	\N
\.

COPY inbound_numbers (id, number, provider, service_id, active, created_at, updated_at) FROM stdin;
7d79137b-eb13-45f9-a5ec-8c2a27e00178	07700900500	mmg	34b725f0-1f47-49bc-a9f5-aa2a84587c53	t	2019-03-25 00:00:00	2019-03-25 15:20:26.028625
\.

COPY templates (id, name, template_type, created_at, updated_at, content, service_id, subject, created_by_id, version, archived, process_type, service_letter_contact_id, hidden, postage, broadcast_data) FROM stdin;
75a02fb0-177a-4d10-89f8-e28e48ede6e5	Functional Tests - CSV Email Template with Jenkins Build ID	email	2019-03-25 15:23:07.172674	\N	The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).	34b725f0-1f47-49bc-a9f5-aa2a84587c53	Functional Tests - CSV Email	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	f	normal	\N	f	\N	\N
63d41316-1c0a-415b-968b-8211a71ab7f1	Functional Tests - CSV SMS Template with Jenkins Build ID	sms	2019-03-25 15:24:14.907439	\N	The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).	34b725f0-1f47-49bc-a9f5-aa2a84587c53	\N	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	f	normal	\N	f	\N	\N
c3caccab-b066-4a43-8340-cae8b2887e86	Functional Tests - CSV Letter Template with Jenkins Build ID	letter	2019-03-25 15:24:40.689266	2019-03-25 15:26:51.614382	The quick brown fox jumped over the lazy dog. Jenkins build id: ((build_id)).	34b725f0-1f47-49bc-a9f5-aa2a84587c53	Functional Tests - CSV Letter	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	2	f	normal	\N	f	second	\N
\.

COPY permissions (id, service_id, user_id, permission, created_at) FROM stdin;
3fc289ea-534e-4f39-94bc-59d42d21d6bd	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	manage_users	2019-03-25 15:02:40.878539
16dd373c-64a1-4700-b6df-08d2959aa749	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	manage_templates	2019-03-25 15:02:40.879226
570003b0-a97b-430c-a443-7155bc23cdf2	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	manage_settings	2019-03-25 15:02:40.879746
439206ff-1dc8-446c-9810-f6f26712bcd4	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	send_texts	2019-03-25 15:02:40.880256
4e962889-19b4-47ec-a511-e1783a664b07	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	send_emails	2019-03-25 15:02:40.880833
7cc0ec67-5599-44ac-abfb-fd920f686337	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	send_letters	2019-03-25 15:02:40.881388
93c7b383-18fe-45c8-aa85-84c6f8f8dc9e	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	manage_api_keys	2019-03-25 15:02:40.881911
593307cd-98fb-4551-a1d9-915a8f83de48	34b725f0-1f47-49bc-a9f5-aa2a84587c53	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	view_activity	2019-03-25 15:02:40.882341
e02d1c3e-613a-46d0-bbbb-b3e341444cdb	34b725f0-1f47-49bc-a9f5-aa2a84587c53	0ebf8f7d-c511-498c-9762-41c4d47507ec	send_letters	2019-03-25 15:12:54.04708
852efe3e-545a-4cb5-a29e-349b76a469eb	34b725f0-1f47-49bc-a9f5-aa2a84587c53	0ebf8f7d-c511-498c-9762-41c4d47507ec	view_activity	2019-03-25 15:12:54.047802
5127e9f1-70db-4029-a64f-0457c10ef4c2	34b725f0-1f47-49bc-a9f5-aa2a84587c53	0ebf8f7d-c511-498c-9762-41c4d47507ec	send_texts	2019-03-25 15:12:54.048362
9ae0be89-c2bd-4702-9b56-036624801719	34b725f0-1f47-49bc-a9f5-aa2a84587c53	0ebf8f7d-c511-498c-9762-41c4d47507ec	send_emails	2019-03-25 15:12:54.048883
57e897b2-a5e2-4e09-bd1b-fd655ea0d2a9	8e1d56fa-12a8-4d00-bed2-db47180bed0a	0d2e9b87-9c54-448c-b549-f764231ee599	create_broadcasts	2021-07-14 14:53:00.40982
85b443b3-2d07-476f-9740-220187f12305	8e1d56fa-12a8-4d00-bed2-db47180bed0a	0d2e9b87-9c54-448c-b549-f764231ee599	manage_templates	2021-07-14 14:53:00.409842
f2060ce7-7966-45a1-b5e1-17aedc93af18	8e1d56fa-12a8-4d00-bed2-db47180bed0a	0d2e9b87-9c54-448c-b549-f764231ee599	cancel_broadcasts	2021-07-14 14:53:00.409852
d9488323-0ad7-4489-a69f-cf1afc4c24c2	8e1d56fa-12a8-4d00-bed2-db47180bed0a	0d2e9b87-9c54-448c-b549-f764231ee599	view_activity	2021-07-14 14:53:00.409881
ea0ec5d2-ce6c-4499-98d7-60a94fd72800	8e1d56fa-12a8-4d00-bed2-db47180bed0a	0d2e9b87-9c54-448c-b549-f764231ee599	reject_broadcasts	2021-07-14 14:53:00.409891
4866284f-9414-4f5a-954e-131b189d235f	8e1d56fa-12a8-4d00-bed2-db47180bed0a	1048af40-45f6-4249-a670-df72ba3352d7	cancel_broadcasts	2021-07-14 14:53:00.409852
1b15bb85-52fc-43da-8365-4364103ffc7f	8e1d56fa-12a8-4d00-bed2-db47180bed0a	1048af40-45f6-4249-a670-df72ba3352d7	view_activity	2021-07-14 14:53:00.409881
4be6e744-efea-4b8b-8af9-0d6c66de628b	8e1d56fa-12a8-4d00-bed2-db47180bed0a	1048af40-45f6-4249-a670-df72ba3352d7	reject_broadcasts	2021-07-14 14:53:00.409891
307aaac1-66b0-48b1-aff1-7029be941a03	8e1d56fa-12a8-4d00-bed2-db47180bed0a	1048af40-45f6-4249-a670-df72ba3352d7	approve_broadcasts	2021-07-14 14:53:00.409891
\.


COPY service_broadcast_settings (service_id, channel, created_at, updated_at, provider) FROM stdin;
8e1d56fa-12a8-4d00-bed2-db47180bed0a	severe	2021-07-14 14:37:35.103872	\N	all
\.


COPY service_email_reply_to (id, service_id, email_address, is_default, created_at, updated_at, archived) FROM stdin;
9640a2c9-2438-4b27-9c1a-31bf73107422	34b725f0-1f47-49bc-a9f5-aa2a84587c53	notify-tests-preview+local-reply-to@digital.cabinet-office.gov.uk	f	2019-03-25 15:08:45.679181	2019-03-25 15:09:35.049148	f
47843c11-471e-446a-94ca-f783b6201078	34b725f0-1f47-49bc-a9f5-aa2a84587c53	notify-tests-preview+local-reply-to-default@digital.cabinet-office.gov.uk	t	2019-03-25 15:09:35.04979	\N	f
\.

COPY service_permissions (service_id, permission, created_at) FROM stdin;
34b725f0-1f47-49bc-a9f5-aa2a84587c53	sms	2019-03-25 15:02:40.883347
34b725f0-1f47-49bc-a9f5-aa2a84587c53	email	2019-03-25 15:02:40.883352
34b725f0-1f47-49bc-a9f5-aa2a84587c53	letter	2019-03-25 15:02:40.883354
34b725f0-1f47-49bc-a9f5-aa2a84587c53	international_sms	2019-03-25 15:02:40.883356
34b725f0-1f47-49bc-a9f5-aa2a84587c53	email_auth	2019-03-25 15:10:35.734382
34b725f0-1f47-49bc-a9f5-aa2a84587c53	inbound_sms	2019-03-25 15:20:26.075574
34b725f0-1f47-49bc-a9f5-aa2a84587c53	edit_folder_permissions	2019-03-25 15:35:17.196132
8e1d56fa-12a8-4d00-bed2-db47180bed0a	broadcast	2021-07-14 14:37:35.112856
\.

COPY service_sms_senders (id, sms_sender, service_id, is_default, inbound_number_id, created_at, updated_at, archived) FROM stdin;
b259392d-94ad-450c-9fdc-fbfc61bf32f8	07700900500	34b725f0-1f47-49bc-a9f5-aa2a84587c53	t	7d79137b-eb13-45f9-a5ec-8c2a27e00178	2019-03-25 15:02:40.886024	2019-03-25 15:20:26.035965	f
bdf151d6-2fd7-4c7f-96e5-4a23a373d13a	func tests	34b725f0-1f47-49bc-a9f5-aa2a84587c53	f	\N	2019-03-25 16:59:56.19595	2019-03-25 17:00:00.120434	f
1f54be97-48f5-4a57-afdb-b548dbba477a	development	8e1d56fa-12a8-4d00-bed2-db47180bed0a	t	\N	2021-07-14 14:36:03.457803	\N	f
\.

COPY services_history (id, name, created_at, updated_at, active, message_limit, restricted, email_from, created_by_id, version, research_mode, organisation_type, prefix_sms, crown, rate_limit, contact_link, consent_to_research, volume_email, volume_letter, volume_sms, count_as_live, go_live_at, go_live_user_id, organisation_id, notes, billing_contact_email_addresses, billing_contact_names, billing_reference, purchase_order_number) FROM stdin;
8e1d56fa-12a8-4d00-bed2-db47180bed0a	Functional Tests Broadcast Service	2021-07-14 14:36:03.423486	\N	t	50	t	functional.tests.broadcast.service	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	1	f	central	t	\N	3000	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N
8e1d56fa-12a8-4d00-bed2-db47180bed0a	Functional Tests Broadcast Service	2021-07-14 14:36:03.423486	2021-07-14 14:37:35.234642	t	50	f	functional.tests.broadcast.service	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	2	f	central	t	\N	3000	\N	\N	\N	\N	\N	f	2021-07-14 14:37:35.122431	\N	38e4bf69-93b0-445d-acee-53ea53fe02df	\N	\N	\N	\N	\N
\.

COPY template_redacted (template_id, redact_personalisation, updated_at, updated_by_id) FROM stdin;
75a02fb0-177a-4d10-89f8-e28e48ede6e5	f	2019-03-25 15:23:07.17662	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b
63d41316-1c0a-415b-968b-8211a71ab7f1	f	2019-03-25 15:24:14.910986	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b
c3caccab-b066-4a43-8340-cae8b2887e86	f	2019-03-25 15:24:40.69439	c76a2961-08dc-4ec5-ac07-57ec9d7cef1b
\.

COPY user_to_service (user_id, service_id) FROM stdin;
c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	34b725f0-1f47-49bc-a9f5-aa2a84587c53
0ebf8f7d-c511-498c-9762-41c4d47507ec	34b725f0-1f47-49bc-a9f5-aa2a84587c53
0d2e9b87-9c54-448c-b549-f764231ee599	8e1d56fa-12a8-4d00-bed2-db47180bed0a
1048af40-45f6-4249-a670-df72ba3352d7	8e1d56fa-12a8-4d00-bed2-db47180bed0a
\.

COPY user_to_organisation (user_id, organisation_id) FROM stdin;
c76a2961-08dc-4ec5-ac07-57ec9d7cef1b	e6e6ce48-f634-4ebf-af7b-c70fdf16cbd5
\.
