# this job can be run separately 
# this job generates reports from the total cleaned scraped data intaken from intakejob and stored in DB
# reports are then also stored within the DB, for access via the outbound API

# business logic layer

# run steps are
# intake - batching - preprocessing - keyword selection - store in SQLite - modelling - prediction/inference
#                                                 our python script is here ^