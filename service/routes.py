"""
Account Service

This microservice handles the lifecycle of Accounts
"""
from flask import jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application

# Ensure all routes are defined only once
app.url_map.strict_slashes = False


############################################################
# Health Endpoint
############################################################
@app.route("/health", methods=["GET"])
def health():
    """Health Status"""
    app.logger.info("Health endpoint called")
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/", methods=["GET"])
def root_index():
    """Root URL response"""
    app.logger.info("Root URL called")
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    try:
        account = Account()
        account.deserialize(request.get_json())
        account.create()
        message = account.serialize()
        location_url = url_for("get_accounts", account_id=account.id, _external=True)
        app.logger.info("Account created with id: %s", account.id)
        return make_response(
            jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
        )
    except KeyError as e:
        app.logger.error("KeyError while creating account: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, "Invalid input: missing required fields")
    except Exception as e:
        app.logger.error("Error creating account: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")


######################################################################
# LIST ALL ACCOUNTS
######################################################################
@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List all Accounts
    This endpoint will list all Accounts
    """
    app.logger.info("Request to list Accounts")
    try:
        accounts = Account.all()
        account_list = [account.serialize() for account in accounts]
        app.logger.info("Returning [%s] accounts", len(account_list))
        return jsonify(account_list), status.HTTP_200_OK
    except Exception as e:
        app.logger.error("Error listing accounts: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")


######################################################################
# READ AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):
    """
    Reads an Account
    This endpoint will read an Account based the account_id that is requested
    """
    app.logger.info("Request to read an Account with id: %s", account_id)
    try:
        account = Account.find(account_id)
        if not account:
            app.logger.warning("Account with id [%s] not found", account_id)
            abort(status.HTTP_404_NOT_FOUND, f"Account with id [{account_id}] could not be found.")
        return jsonify(account.serialize()), status.HTTP_200_OK
    except Exception as e:
        app.logger.error("Error reading account: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_accounts(account_id):
    """
    Update an Account
    This endpoint will update an Account based on the posted data
    """
    app.logger.info("Request to update an Account with id: %s", account_id)
    try:
        account = Account.find(account_id)
        if not account:
            app.logger.warning("Account with id [%s] not found for update", account_id)
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Account with id [{account_id}] could not be found.",
            )
        account.deserialize(request.get_json())
        account.update()
        app.logger.info("Account with id [%s] updated", account_id)
        return jsonify(account.serialize()), status.HTTP_200_OK
    except KeyError as e:
        app.logger.error("KeyError while updating account: %s", str(e))
        abort(status.HTTP_400_BAD_REQUEST, "Invalid input: missing required fields")
    except Exception as e:
        app.logger.error("Error updating account: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")


######################################################################
# DELETE AN ACCOUNT
######################################################################
@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_accounts(account_id):
    """
    Delete an Account
    This endpoint will delete an Account based on the account_id that is requested
    """
    app.logger.info("Request to delete an Account with id: %s", account_id)
    try:
        account = Account.find(account_id)
        if account:
            account.delete()
            app.logger.info("Account with id [%s] deleted", account_id)
        else:
            app.logger.warning("Account with id [%s] not found for deletion", account_id)
        return "", status.HTTP_204_NO_CONTENT
    except Exception as e:
        app.logger.error("Error deleting account: %s", str(e))
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
