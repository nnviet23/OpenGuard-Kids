from enforcement import apply_policy_status, enforcement_enabled

def test_enforcement_disabled_is_dry_run():
    called = []
    result = apply_policy_status("QUOTA_EXCEEDED", enabled=False, already_locked=False, lock_function=lambda: called.append(True) or True)
    assert result == "DRY_RUN"
    assert called == []

def test_blocking_status_requests_lock_when_enabled():
    called = []
    result = apply_policy_status("OUTSIDE_ALLOWED_SCHEDULE", enabled=True, already_locked=False, lock_function=lambda: called.append(True) or True)
    assert result == "LOCK_REQUESTED"
    assert called == [True]

def test_already_locked_does_not_repeat_lock():
    called = []
    result = apply_policy_status("QUOTA_EXCEEDED", enabled=True, already_locked=True, lock_function=lambda: called.append(True) or True)
    assert result == "LOCKED_ALREADY"
    assert called == []

def test_allowed_does_not_lock():
    called = []
    result = apply_policy_status("ALLOWED", enabled=True, already_locked=False, lock_function=lambda: called.append(True) or True)
    assert result == "NO_LOCK_REQUIRED"
    assert called == []

def test_disabled_policy_does_not_lock():
    called = []
    result = apply_policy_status("POLICY_DISABLED", enabled=True, already_locked=False, lock_function=lambda: called.append(True) or True)
    assert result == "NO_LOCK_REQUIRED"
    assert called == []

def test_invalid_policy_requires_review_without_lock():
    called = []
    result = apply_policy_status("INVALID_POLICY", enabled=True, already_locked=False, lock_function=lambda: called.append(True) or True)
    assert result == "POLICY_REVIEW_REQUIRED"
    assert called == []

def test_lock_failure_is_reported():
    result = apply_policy_status("QUOTA_EXCEEDED", enabled=True, already_locked=False, lock_function=lambda: False)
    assert result == "LOCK_FAILED"

def test_environment_flag_is_opt_in():
    assert enforcement_enabled("0") is False
    assert enforcement_enabled("1") is True
