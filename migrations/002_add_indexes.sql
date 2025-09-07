-- Performance indexes for the medical referral system

-- Indexes for efficient queries
create index if not exists idx_patients_patient_id on
   patients (
      patient_id
   );
create index if not exists idx_referrals_patient_id on
   referral_requests (
      patient_id
   );
create index if not exists idx_referrals_date on
   referral_requests (
      referral_date
   );
create index if not exists idx_referrals_created_at on
   referral_requests (
      created_at
   );
create index if not exists idx_referrals_urgency on
   referral_requests (
      urgency_level
   );
create index if not exists idx_referrals_specialty on
   referral_requests (
      specialty
   );
create index if not exists idx_referrals_status on
   referral_requests (
      status
   );
create index if not exists idx_query_logs_referral_id on
   query_logs (
      referral_request_id
   );
create index if not exists idx_query_logs_type on
   query_logs (
      query_type
   );