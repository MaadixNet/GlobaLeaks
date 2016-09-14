# -*- encoding: utf-8 -*-
from collections import OrderedDict
import importlib
import os
import shutil

from storm.locals import create_database, Store

from globaleaks import models, DATABASE_VERSION, FIRST_DATABASE_VERSION_SUPPORTED
from globaleaks.models import l10n, config
from globaleaks.settings import GLSettings
from globaleaks.db import db_manage_version_update
from globaleaks import security

from globaleaks.db.migrations.update_16 import Receiver_v_15, Notification_v_15
from globaleaks.db.migrations.update_17 import Node_v_16, Receiver_v_16, Notification_v_16, Stats_v_16
from globaleaks.db.migrations.update_18 import Node_v_17
from globaleaks.db.migrations.update_19 import Node_v_18
from globaleaks.db.migrations.update_20 import Node_v_19, Notification_v_19, Comment_v_19, Message_v_19, \
    InternalTip_v_19, ReceiverTip_v_19, InternalFile_v_19, ReceiverFile_v_19, Receiver_v_19, Context_v_19
from globaleaks.db.migrations.update_21 import Node_v_20, Notification_v_20, Receiver_v_20, User_v_20, \
    Context_v_20, Step_v_20, Field_v_20, FieldOption_v_20, InternalTip_v_20
from globaleaks.db.migrations.update_22 import Context_v_21, InternalTip_v_21
from globaleaks.db.migrations.update_23 import InternalFile_v_22, Comment_v_22, Context_v_22, \
    Field_v_22, FieldOption_v_22, Notification_v_22, InternalTip_v_22
from globaleaks.db.migrations.update_24 import User_v_23, Receiver_v_23, Node_v_23, Notification_v_23, \
    Context_v_23, InternalTip_v_23, Step_v_23, Field_v_23, ArchivedSchema_v_23, ReceiverTip_v_23
from globaleaks.db.migrations.update_25 import User_v_24
from globaleaks.db.migrations.update_26 import InternalFile_v_25
from globaleaks.db.migrations.update_27 import Node_v_26, Context_v_26, Notification_v_26
from globaleaks.db.migrations.update_28 import Field_v_27, Step_v_27, FieldField_v_27, StepField_v_27, FieldOption_v_27
from globaleaks.db.migrations.update_29 import Context_v_28, Node_v_28
from globaleaks.db.migrations.update_30 import Node_v_29, Context_v_29, Step_v_29, FieldAnswer_v_29, FieldAnswerGroup_v_29, FieldAnswerGroupFieldAnswer_v_29
from globaleaks.db.migrations.update_31 import Node_v_30, Context_v_30, User_v_30, ReceiverTip_v_30, Notification_v_30
from globaleaks.db.migrations.update_32 import Node_v_31, Comment_v_31, Message_v_31, User_v_31
from globaleaks.db.migrations.update_33 import Node_v_32, WhistleblowerTip_v_32, InternalTip_v_32, User_v_32
from globaleaks.db.migrations.update_34 import Node_v_33, Notification_v_33


migration_mapping = OrderedDict([
    ('Anomalies', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, models.Anomalies, 0, 0, 0, 0]),
    ('ArchivedSchema', [-1, -1, -1, -1, -1, -1, -1, -1, ArchivedSchema_v_23, models.ArchivedSchema, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('ApplicationData', [-1, -1, -1, -1, -1, -1, -1, -1, -1, models.ApplicationData, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('Comment', [Comment_v_19, 0, 0, 0, 0, Comment_v_22, 0, 0, Comment_v_31, 0, 0, 0, 0, 0, 0, 0, 0, models.Comment, 0, 0]),
    ('Context', [Context_v_19, 0, 0, 0, 0, Context_v_20, Context_v_21, Context_v_22, Context_v_23, Context_v_26, 0, 0, Context_v_28, 0, Context_v_29, Context_v_30, models.Context, 0, 0, 0]),
    ('CustomTexts', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, models.CustomTexts, 0, 0]),
    ('EnabledLanguage', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, l10n.EnabledLanguage]),
    ('Field', [Field_v_20, 0, 0, 0, 0, 0, Field_v_22, 0, Field_v_23, Field_v_27, 0, 0, 0, models.Field, 0, 0, 0, 0, 0, 0]),
    ('FieldAnswer', [-1, -1, -1, -1, -1, -1, -1, -1, FieldAnswer_v_29, 0, 0, 0, 0, 0, 0, models.FieldAnswer, 0, 0, 0, 0]),
    ('FieldAnswerGroup', [-1, -1, -1, -1, -1, -1, -1, -1, FieldAnswerGroup_v_29, 0, 0, 0, 0, 0, 0, models.FieldAnswerGroup, 0, 0, 0, 0]),
    ('FieldAnswerGroupFieldAnswer', [-1, -1, -1, -1, -1, -1, -1, -1, FieldAnswerGroupFieldAnswer_v_29, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1]),
    ('FieldAttr', [-1, -1, -1, -1, -1, -1, -1, -1, models.FieldAttr, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('FieldField', [FieldField_v_27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1]),
    ('FieldOption', [FieldOption_v_20, 0, 0, 0, 0, 0, FieldOption_v_22, 0, FieldOption_v_27, 0, 0, 0, 0, models.FieldOption, 0, 0, 0, 0, 0, 0]),
    ('File', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, models.File, 0, 0, 0]),
    ('IdentityAccessRequest', [-1, -1, -1, -1, -1, -1, -1, -1, -1, models.IdentityAccessRequest, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('InternalFile', [InternalFile_v_19, 0, 0, 0, 0, InternalFile_v_22, 0, 0, InternalFile_v_25, 0, 0, models.InternalFile, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('InternalTip', [InternalTip_v_19, 0, 0, 0, 0, InternalTip_v_20, InternalTip_v_21, InternalTip_v_22, InternalTip_v_23, InternalTip_v_32, 0, 0, 0, 0, 0, 0, 0, 0, models.InternalTip, 0]),
    ('Mail', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, models.Mail, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('Message', [Message_v_19, 0, 0, 0, 0, Message_v_31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, models.Message, 0, 0]),
    ('Node', [Node_v_16, 0, Node_v_17, Node_v_18, Node_v_19, Node_v_20, Node_v_23, 0, 0, Node_v_26, 0, 0, Node_v_28, 0, Node_v_29, Node_v_30, Node_v_31, Node_v_32, Node_v_33, -1]),
    ('Notification', [Notification_v_15, Notification_v_16, Notification_v_19, 0, 0, Notification_v_20, Notification_v_22, 0, Notification_v_23, Notification_v_26, 0, 0, Notification_v_30, 0, 0, 0, Notification_v_33, 0, 0, -1]),
    ('Questionnaire', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, models.Questionnaire, 0, 0, 0, 0]),
    ('Receiver', [Receiver_v_15, Receiver_v_16, Receiver_v_19, 0, 0, Receiver_v_20, Receiver_v_23, 0, 0, models.Receiver, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('ReceiverContext', [models.ReceiverContext, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('ReceiverFile', [ReceiverFile_v_19, 0, 0, 0, 0, models.ReceiverFile, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('ReceiverTip', [ReceiverTip_v_19, 0, 0, 0, 0, ReceiverTip_v_23, 0, 0, 0, ReceiverTip_v_30, 0, 0, 0, 0, 0, 0, models.ReceiverTip, 0, 0, 0]),
    ('Config', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, config.Config]),
    ('ConfigL10N', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, l10n.ConfigL10N]),
    ('Step', [Step_v_20, 0, 0, 0, 0, 0, Step_v_23, 0, 0, Step_v_27, 0, 0, 0, Step_v_29, 0, models.Step, 0, 0, 0, 0]),
    ('StepField', [StepField_v_27, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1]),
    ('SecureFileDelete', [-1, -1, -1, -1, -1, -1, -1, -1, -1, models.SecureFileDelete, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('Stats', [Stats_v_16, 0, models.Stats, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ('User', [User_v_20, 0, 0, 0, 0, 0, User_v_23, 0, 0, User_v_24, User_v_30, 0, 0, 0, 0, 0, User_v_31, User_v_32, models.User, 0]),
    ('WhistleblowerTip', [WhistleblowerTip_v_32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, models.WhistleblowerTip, 0])
])


def perform_schema_migration(version):
    """
    @param version:
    @return:
    """
    to_delete_on_fail = []
    to_delete_on_success = []

    if version < FIRST_DATABASE_VERSION_SUPPORTED:
        GLSettings.print_msg("Migrations from DB version lower than %d are no longer supported!" % FIRST_DATABASE_VERSION_SUPPORTED)
        quit()

    tmpdir =  os.path.abspath(os.path.join(GLSettings.db_path, 'tmp'))
    orig_db_file = os.path.abspath(os.path.join(GLSettings.db_path, 'glbackend-%d.db' % version))
    final_db_file = os.path.abspath(os.path.join(GLSettings.db_path, 'glbackend-%d.db' % DATABASE_VERSION))

    shutil.rmtree(tmpdir, True)
    os.mkdir(tmpdir)
    shutil.copy2(orig_db_file, tmpdir)

    old_db_file = None
    new_db_file = None


    try:
        while version < DATABASE_VERSION:
            old_db_file = os.path.abspath(os.path.join(tmpdir, 'glbackend-%d.db' % version))
            new_db_file = os.path.abspath(os.path.join(tmpdir, 'glbackend-%d.db' % (version + 1)))

            GLSettings.db_file = new_db_file
            GLSettings.enable_input_length_checks = False

            to_delete_on_fail.append(new_db_file)
            to_delete_on_success.append(old_db_file)

            GLSettings.print_msg("Updating DB from version %d to version %d" % (version, version + 1))

            store_old = Store(create_database('sqlite:' + old_db_file))
            store_new = Store(create_database('sqlite:' + new_db_file))

            # Here is instanced the migration script
            MigrationModule = importlib.import_module("globaleaks.db.migrations.update_%d" % (version + 1))
            migration_script = MigrationModule.MigrationScript(migration_mapping, version, store_old, store_new)

            GLSettings.print_msg("Migrating table:")

            try:
                try:
                    migration_script.prologue()
                except Exception as exception:
                    GLSettings.print_msg("Failure while executing migration prologue: %s" % exception)
                    raise exception

                for model_name, _ in migration_mapping.iteritems():
                    if migration_script.model_from[model_name] is not None and migration_script.model_to[model_name] is not None:
                        try:
                            migration_script.migrate_model(model_name)

                            # Commit at every table migration in order to be able to detect
                            # the precise migration that may fail.
                            migration_script.commit()
                        except Exception as exception:
                            GLSettings.print_msg("Failure while migrating table %s: %s " % (model_name, exception))
                            raise exception
                try:
                    migration_script.epilogue()
                    migration_script.commit()
                except Exception as exception:
                    GLSettings.print_msg("Failure while executing migration epilogue: %s " % exception)
                    raise exception

            finally:
                # the database should be always closed before leaving the application
                # in order to not keep leaking journal files.
                migration_script.close()

            GLSettings.print_msg("Migration stats:")

            # we open a new db in order to verify integrity of the generated file
            store_verify = Store(create_database(GLSettings.make_db_uri(new_db_file)))

            for model_name, _ in migration_mapping.iteritems():
                if model_name == 'ApplicationData':
                    continue

                if migration_script.model_from[model_name] is not None and migration_script.model_to[model_name] is not None:
                     count = store_verify.find(migration_script.model_to[model_name]).count()
                     if migration_script.entries_count[model_name] != count:
                         if migration_script.fail_on_count_mismatch[model_name]:
                             raise AssertionError("Integrity check failed on count equality for table %s: %d != %d" % \
                                                  (model_name, count, migration_script.entries_count[model_name]))
                         else:
                             GLSettings.print_msg(" * %s table migrated (entries count changed from %d to %d)" % \
                                                  (model_name, migration_script.entries_count[model_name], count))
                     else:
                         GLSettings.print_msg(" * %s table migrated (%d entry(s))" % \
                                              (model_name, migration_script.entries_count[model_name]))

            version += 1

            store_verify.close()

        ### END-WHILE ### The tmp-db is now at the latest version ###
        new_tmp_store = Store(create_database(GLSettings.make_db_uri(new_db_file)))
        try:
            db_manage_version_update(new_tmp_store)
            new_tmp_store.commit()
        except:
            new_tmp_store.rollback()
            new_tmp_store.close()
            raise
        finally:
            new_tmp_store.close()

    except Exception as exception:
        # simply propagate the exception
        raise exception

    else:
        # in case of success first copy the new migrated db, then as last action delete the original db file
        shutil.copy(new_db_file, final_db_file)
        security.overwrite_and_remove(orig_db_file)

    finally:
        # Always cleanup the temporary directory used for the migration
        for f in os.listdir(tmpdir):
            tmp_db_file = os.path.join(tmpdir, f)
            security.overwrite_and_remove(tmp_db_file)
        shutil.rmtree(tmpdir)
