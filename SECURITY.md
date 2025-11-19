# Security Policy

## Overview

Auto Edit takes security seriously. This document outlines security considerations and best practices when using Auto Edit.

## Security Features

### 1. Path Traversal Protection

Auto Edit implements path validation to prevent directory traversal attacks:

- **Path Canonicalization**: All file paths are resolved to absolute canonical paths using `Path.resolve()`
- **Directory Validation**: Paths are validated to ensure they stay within expected directories
- **Input Sanitization**: User-provided paths are sanitized before use

**Example Protection:**
```python
# Prevents attacks like: ../../etc/passwd
# Prevents symlink attacks
# Validates paths stay within allowed directories
```

### 2. Pickle Deserialization Safety

Auto Edit uses Python's `pickle` module for ML model storage. Security measures include:

- **Path Validation**: Only loads pickle files from designated model/training directories
- **Structure Validation**: Validates pickle content structure after loading
- **Error Handling**: Graceful handling of corrupted or malicious pickle files

**Important Warning:**
> ⚠️ **Never load pickle files (.pkl) from untrusted sources!**
> Pickle can execute arbitrary code during deserialization.

**Safe Usage:**
- Only use models you created yourself with Auto Edit
- Only use training examples you created yourself
- Don't download and load .pkl files from the internet
- Keep your `./models/` and `./training_data/` directories secure

### 3. Command Injection Protection

Auto Edit is protected against command injection:

- **No Shell Execution**: All subprocess calls use list format, never `shell=True`
- **No `os.system()`**: Direct system calls are avoided
- **No Dynamic Code**: No use of `eval()` or `exec()`
- **Safe FFmpeg Calls**: All FFmpeg parameters are passed as list arguments

### 4. YAML Configuration Safety

- **Safe Loading**: Uses `yaml.safe_load()` instead of unsafe `yaml.load()`
- **Type Validation**: Configuration values are validated
- **Environment Variable Override**: Supports secure environment-based configuration

## Best Practices

### For Users

1. **File Sources**
   - Only process video files from trusted sources
   - Be cautious with videos from unknown origins
   - Don't process files with suspicious names or paths

2. **Model Files**
   - Only use models you trained yourself
   - Don't share or download model (.pkl) files
   - Keep your models directory secure

3. **Configuration**
   - Review `config.yaml` before making changes
   - Use environment variables for sensitive paths
   - Keep configuration files in version control (without secrets)

4. **Output Directories**
   - Use dedicated output directories
   - Don't output to system directories
   - Regularly clean up temporary files

### For Developers

1. **Code Review**
   - Review all file operations for path validation
   - Never use `shell=True` in subprocess calls
   - Validate all user inputs

2. **Dependencies**
   - Keep dependencies up to date
   - Review dependency security advisories
   - Use virtual environments

3. **Testing**
   - Test with malicious file names
   - Test path traversal attempts
   - Validate error handling

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Contact the maintainers privately
3. Provide detailed reproduction steps
4. Allow time for a fix before public disclosure

## Security Checklist

- [x] Path traversal protection
- [x] Pickle deserialization validation
- [x] Command injection prevention
- [x] Safe YAML loading
- [x] Input validation
- [x] Error handling
- [ ] Rate limiting (not applicable for desktop app)
- [ ] Authentication (not applicable for desktop app)

## Known Limitations

1. **Pickle Files**: Inherently unsafe format, use only with trusted data
2. **Video Processing**: Large video files can consume significant system resources
3. **FFmpeg**: Security depends on FFmpeg version being up to date

## Updates

- **2024-01**: Initial security features implemented
  - Path validation and sanitization
  - Pickle file validation
  - Command injection protection
  - Safe YAML loading

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/pickle.html#module-pickle)
- [FFmpeg Security](https://ffmpeg.org/security.html)
