import 'package:flutter/material.dart';
import '../config/cpcb_theme.dart';
import '../providers/app_state.dart';

class LoginScreen extends StatefulWidget {
  final AppState state;

  const LoginScreen({super.key, required this.state});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();

  // Mode: true = Sign In, false = Sign Up
  bool _isSignIn = true;

  // Controllers
  final _emailController = TextEditingController(text: 'ecoair@infosys.com');
  final _passwordController = TextEditingController(text: 'password123');
  final _confirmPasswordController = TextEditingController();
  final _nameController = TextEditingController();

  // Form options
  bool _obscurePassword = true;
  bool _obscureConfirmPassword = true;
  bool _rememberMe = true;
  bool _isLoading = false;
  String? _errorMessage;

  String _selectedHealthProfile = 'General User';

  final List<Map<String, String>> _healthProfiles = [
    {
      'id': 'General User',
      'label': 'General Public',
      'icon': '👤',
      'desc': 'Standard inhalation rate (1.0×)',
    },
    {
      'id': 'Asthmatic / Respiratory',
      'label': 'Asthmatic / Respiratory',
      'icon': '🫁',
      'desc': 'High sensitivity (1.4× exposure factor)',
    },
    {
      'id': 'Elderly (60+ Years)',
      'label': 'Senior Citizen (60+)',
      'icon': '👴',
      'desc': 'Elevated vulnerability (1.3× exposure factor)',
    },
    {
      'id': 'Child (Under 12 Years)',
      'label': 'Children (<12 Years)',
      'icon': '👶',
      'desc': 'Rapid ventilation (1.2× exposure factor)',
    },
  ];

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _switchMode(bool signIn) {
    setState(() {
      _isSignIn = signIn;
      _errorMessage = null;
      if (!signIn) {
        if (_nameController.text.isEmpty) _nameController.text = 'Harika K.';
        _confirmPasswordController.text = _passwordController.text;
      }
    });
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      if (_isSignIn) {
        final err = await widget.state.login(
          _emailController.text,
          _passwordController.text,
          rememberMe: _rememberMe,
        );

        if (mounted) {
          if (err != null) {
            setState(() {
              _errorMessage = err;
              _isLoading = false;
            });
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Row(
                  children: [
                    const Icon(Icons.check_circle_outline, color: Colors.white, size: 20),
                    const SizedBox(width: 8),
                    Text('Welcome back, ${widget.state.currentUser?.name ?? "User"}!'),
                  ],
                ),
                backgroundColor: CpcbTheme.cpcbGood,
                behavior: SnackBarBehavior.floating,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            );
          }
        }
      } else {
        // Sign Up
        if (_passwordController.text != _confirmPasswordController.text) {
          setState(() {
            _errorMessage = 'Passwords do not match.';
            _isLoading = false;
          });
          return;
        }

        final err = await widget.state.register(
          email: _emailController.text,
          password: _passwordController.text,
          name: _nameController.text,
          healthProfile: _selectedHealthProfile,
        );

        if (mounted) {
          if (err != null) {
            setState(() {
              _errorMessage = err;
              _isLoading = false;
            });
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Row(
                  children: [
                    const Icon(Icons.celebration, color: Colors.white, size: 20),
                    const SizedBox(width: 8),
                    Text('Account created for ${_nameController.text}!'),
                  ],
                ),
                backgroundColor: CpcbTheme.primaryBlue,
                behavior: SnackBarBehavior.floating,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            );
          }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = 'An unexpected error occurred: $e';
          _isLoading = false;
        });
      }
    }
  }

  void _showForgotPasswordDialog() {
    final resetEmailController = TextEditingController(text: _emailController.text);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
        title: const Row(
          children: [
            Icon(Icons.lock_reset, color: CpcbTheme.primaryBlue),
            SizedBox(width: 8),
            Text('Reset Password', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter your registered email address to receive password recovery instructions.',
              style: TextStyle(fontSize: 12.5, color: CpcbTheme.textSecondary),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: resetEmailController,
              keyboardType: TextInputType.emailAddress,
              decoration: InputDecoration(
                labelText: 'Email Address',
                hintText: 'user@example.com',
                prefixIcon: const Icon(Icons.email_outlined, size: 20),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Password reset instructions sent to ${resetEmailController.text}'),
                  backgroundColor: CpcbTheme.primaryBlue,
                  behavior: SnackBarBehavior.floating,
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: CpcbTheme.primaryBlue,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Send Reset Link'),
          ),
        ],
      ),
    );
  }

  void _fillDemoCredentials(String email, String password, String name) {
    setState(() {
      _emailController.text = email;
      _passwordController.text = password;
      _confirmPasswordController.text = password;
      _nameController.text = name;
      _errorMessage = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Scaffold(
      backgroundColor: CpcbTheme.backgroundLight,
      body: SingleChildScrollView(
        padding: EdgeInsets.only(bottom: bottomInset + 24),
        child: Column(
          children: [
            // ── Top Gradient Hero Header ─────────────────────────────────────
            _buildHeroHeader(context),

            const SizedBox(height: 16),

            // ── Main Card Form ───────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  border: Border.all(color: CpcbTheme.borderSubtle),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.04),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(22),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      // Segmented Mode Switcher (Sign In vs Sign Up)
                      _buildModeSwitcher(),

                      const SizedBox(height: 20),

                      // Error message banner
                      if (_errorMessage != null) ...[
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEE2E2),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFFCA5A5)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.error_outline, color: Color(0xFFDC2626), size: 18),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _errorMessage!,
                                  style: const TextStyle(
                                    color: Color(0xFF991B1B),
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],

                      // Full Name (Only in Sign Up Mode)
                      if (!_isSignIn) ...[
                        _buildInputField(
                          controller: _nameController,
                          label: 'Full Name',
                          hint: 'Harika K.',
                          prefixIcon: Icons.person_outline,
                          validator: (val) {
                            if (val == null || val.trim().isEmpty) {
                              return 'Please enter your full name';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 14),

                        // Health Vulnerability Profile Selector
                        _buildHealthProfileDropdown(),
                        const SizedBox(height: 14),
                      ],

                      // Email Field
                      _buildInputField(
                        controller: _emailController,
                        label: 'Email Address',
                        hint: 'user@ecoair.org',
                        prefixIcon: Icons.email_outlined,
                        keyboardType: TextInputType.emailAddress,
                        validator: (val) {
                          if (val == null || val.trim().isEmpty) {
                            return 'Please enter your email address';
                          }
                          if (!val.contains('@') || !val.contains('.')) {
                            return 'Please enter a valid email format';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 14),

                      // Password Field
                      _buildInputField(
                        controller: _passwordController,
                        label: 'Password',
                        hint: '••••••••',
                        prefixIcon: Icons.lock_outline,
                        obscureText: _obscurePassword,
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                            size: 19,
                            color: CpcbTheme.textMuted,
                          ),
                          onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                        ),
                        validator: (val) {
                          if (val == null || val.isEmpty) {
                            return 'Please enter your password';
                          }
                          if (val.length < 6) {
                            return 'Password must be at least 6 characters';
                          }
                          return null;
                        },
                      ),

                      // Confirm Password (Only in Sign Up Mode)
                      if (!_isSignIn) ...[
                        const SizedBox(height: 14),
                        _buildInputField(
                          controller: _confirmPasswordController,
                          label: 'Confirm Password',
                          hint: '••••••••',
                          prefixIcon: Icons.lock_reset,
                          obscureText: _obscureConfirmPassword,
                          suffixIcon: IconButton(
                            icon: Icon(
                              _obscureConfirmPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                              size: 19,
                              color: CpcbTheme.textMuted,
                            ),
                            onPressed: () => setState(() => _obscureConfirmPassword = !_obscureConfirmPassword),
                          ),
                          validator: (val) {
                            if (val == null || val.isEmpty) {
                              return 'Please re-enter your password';
                            }
                            if (val != _passwordController.text) {
                              return 'Passwords do not match';
                            }
                            return null;
                          },
                        ),
                      ],

                      const SizedBox(height: 10),

                      // Remember Me & Forgot Password Row (Sign In mode)
                      if (_isSignIn)
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                SizedBox(
                                  width: 24,
                                  height: 24,
                                  child: Checkbox(
                                    value: _rememberMe,
                                    activeColor: CpcbTheme.primaryBlue,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                    onChanged: (v) => setState(() => _rememberMe = v ?? true),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                const Text(
                                  'Remember me',
                                  style: TextStyle(fontSize: 12, color: CpcbTheme.textSecondary, fontWeight: FontWeight.w500),
                                ),
                              ],
                            ),
                            TextButton(
                              onPressed: _showForgotPasswordDialog,
                              style: TextButton.styleFrom(
                                padding: EdgeInsets.zero,
                                visualDensity: VisualDensity.compact,
                              ),
                              child: const Text(
                                'Forgot Password?',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: CpcbTheme.primaryBlue,
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ],
                        ),

                      const SizedBox(height: 16),

                      // Primary Action Button (Sign In / Register)
                      SizedBox(
                        height: 50,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _handleSubmit,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: CpcbTheme.primaryBlue,
                            foregroundColor: Colors.white,
                            elevation: 2,
                            shadowColor: CpcbTheme.primaryBlue.withOpacity(0.4),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                          ),
                          child: _isLoading
                              ? const SizedBox(
                                  width: 20,
                                  height: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2.2, color: Colors.white),
                                )
                              : Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(_isSignIn ? Icons.login : Icons.person_add_alt_1, size: 19),
                                    const SizedBox(width: 8),
                                    Text(
                                      _isSignIn ? 'Sign In to EcoAir' : 'Create Free Account',
                                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800),
                                    ),
                                  ],
                                ),
                        ),
                      ),

                      const SizedBox(height: 16),

                      // Quick Demo Accounts Quick-Fill Pill
                      _buildQuickDemoSection(),
                    ],
                  ),
                ),
              ),
            ),

            const SizedBox(height: 18),

            // Continue as Guest Button
            TextButton.icon(
              onPressed: () {
                widget.state.continueAsGuest();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Logged in as Guest Explorer.'),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              },
              icon: const Icon(Icons.arrow_forward, size: 16, color: CpcbTheme.textSecondary),
              label: const Text(
                'Skip authentication & explore as Guest',
                style: TextStyle(
                  fontSize: 12.5,
                  fontWeight: FontWeight.w600,
                  color: CpcbTheme.textSecondary,
                  decoration: TextDecoration.underline,
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Security Compliance Footer Badge
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.verified_user_outlined, size: 14, color: CpcbTheme.textMuted),
                const SizedBox(width: 5),
                Text(
                  'CPCB Standards Compliant • 256-Bit SSL Secured',
                  style: TextStyle(fontSize: 10.5, color: CpcbTheme.textMuted.withOpacity(0.9), fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // ── Hero Header ─────────────────────────────────────────────────────────────
  Widget _buildHeroHeader(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: EdgeInsets.only(
        top: MediaQuery.of(context).padding.top + 20,
        bottom: 28,
        left: 24,
        right: 24,
      ),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Color(0xFF0F172A),
            Color(0xFF1E293B),
            Color(0xFF2563EB),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.only(
          bottomLeft: Radius.circular(32),
          bottomRight: Radius.circular(32),
        ),
      ),
      child: Column(
        children: [
          // Logo Badge
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white.withOpacity(0.25), width: 1.5),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Center(
              child: Icon(Icons.cloud_sync_outlined, color: Colors.white, size: 34),
            ),
          ),
          const SizedBox(height: 12),

          // Title & Subtitle
          const Text(
            'EcoAir Intelligence',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w900,
              color: Colors.white,
              letterSpacing: 0.2,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            _isSignIn
                ? 'Sign in to access personalized AQI hazard forecasts'
                : 'Register your account to track personal exposure',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 12,
              color: Colors.white.withOpacity(0.8),
              fontWeight: FontWeight.w400,
            ),
          ),
        ],
      ),
    );
  }

  // ── Segmented Mode Switcher ────────────────────────────────────────────────
  Widget _buildModeSwitcher() {
    return Container(
      height: 44,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: () => _switchMode(true),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                decoration: BoxDecoration(
                  color: _isSignIn ? Colors.white : Colors.transparent,
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: _isSignIn
                      ? [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.06),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          )
                        ]
                      : null,
                ),
                child: Center(
                  child: Text(
                    'Sign In',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: _isSignIn ? FontWeight.w800 : FontWeight.w600,
                      color: _isSignIn ? CpcbTheme.primaryBlue : CpcbTheme.textSecondary,
                    ),
                  ),
                ),
              ),
            ),
          ),
          Expanded(
            child: GestureDetector(
              onTap: () => _switchMode(false),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                decoration: BoxDecoration(
                  color: !_isSignIn ? Colors.white : Colors.transparent,
                  borderRadius: BorderRadius.circular(10),
                  boxShadow: !_isSignIn
                      ? [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.06),
                            blurRadius: 6,
                            offset: const Offset(0, 2),
                          )
                        ]
                      : null,
                ),
                child: Center(
                  child: Text(
                    'Register',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: !_isSignIn ? FontWeight.w800 : FontWeight.w600,
                      color: !_isSignIn ? CpcbTheme.primaryBlue : CpcbTheme.textSecondary,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Input Field Helper ─────────────────────────────────────────────────────
  Widget _buildInputField({
    required TextEditingController controller,
    required String label,
    required String hint,
    required IconData prefixIcon,
    Widget? suffixIcon,
    bool obscureText = false,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String?)? validator,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: CpcbTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 6),
        TextFormField(
          controller: controller,
          obscureText: obscureText,
          keyboardType: keyboardType,
          style: const TextStyle(fontSize: 13.5, color: CpcbTheme.textPrimary, fontWeight: FontWeight.w600),
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(fontSize: 13, color: CpcbTheme.textMuted),
            prefixIcon: Icon(prefixIcon, size: 19, color: CpcbTheme.primaryBlue),
            suffixIcon: suffixIcon,
            filled: true,
            fillColor: const Color(0xFFF8FAFC),
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: CpcbTheme.borderSubtle),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: CpcbTheme.primaryBlue, width: 1.8),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFDC2626)),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFDC2626), width: 1.8),
            ),
          ),
          validator: validator,
        ),
      ],
    );
  }

  // ── Health Profile Dropdown ────────────────────────────────────────────────
  Widget _buildHealthProfileDropdown() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Row(
          children: [
            Text(
              'Health Sensitivity Profile',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: CpcbTheme.textPrimary,
              ),
            ),
            SizedBox(width: 4),
            Text('*', style: TextStyle(color: Color(0xFFDC2626), fontWeight: FontWeight.bold)),
          ],
        ),
        const SizedBox(height: 6),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: CpcbTheme.borderSubtle),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: _selectedHealthProfile,
              isExpanded: true,
              icon: const Icon(Icons.keyboard_arrow_down, color: CpcbTheme.primaryBlue),
              items: _healthProfiles.map((p) {
                return DropdownMenuItem<String>(
                  value: p['id'],
                  child: Row(
                    children: [
                      Text(p['icon']!, style: const TextStyle(fontSize: 16)),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              p['label']!,
                              style: const TextStyle(fontSize: 12.5, fontWeight: FontWeight.w700),
                            ),
                            Text(
                              p['desc']!,
                              style: const TextStyle(fontSize: 10, color: CpcbTheme.textMuted),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _selectedHealthProfile = val);
              },
            ),
          ),
        ),
      ],
    );
  }

  // ── Quick Demo Helper Section ──────────────────────────────────────────────
  Widget _buildQuickDemoSection() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFBFDBFE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.bolt, size: 16, color: CpcbTheme.primaryBlue),
              SizedBox(width: 4),
              Text(
                'Quick Demo Test Accounts',
                style: TextStyle(
                  fontSize: 11.5,
                  fontWeight: FontWeight.w800,
                  color: CpcbTheme.primaryBlue,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              _buildDemoPill(
                label: 'General User',
                email: 'ecoair@infosys.com',
                password: 'password123',
                name: 'Harika K.',
              ),
              _buildDemoPill(
                label: 'Asthmatic (1.4×)',
                email: 'asthma.care@airsense.org',
                password: 'password123',
                name: 'Dr. Rohan Verma',
              ),
              _buildDemoPill(
                label: 'Standard Demo',
                email: 'demo@ecoair.org',
                password: 'demo123',
                name: 'AirSense Explorer',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDemoPill({
    required String label,
    required String email,
    required String password,
    required String name,
  }) {
    final isSelected = _emailController.text == email;
    return GestureDetector(
      onTap: () => _fillDemoCredentials(email, password, name),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isSelected ? CpcbTheme.primaryBlue : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? CpcbTheme.primaryBlue : const Color(0xFF93C5FD),
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 10.5,
            fontWeight: FontWeight.w700,
            color: isSelected ? Colors.white : CpcbTheme.primaryBlue,
          ),
        ),
      ),
    );
  }
}
