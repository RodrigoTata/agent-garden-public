# Guía de Referencia: Auditoría Crítica de Software desde la Lógica de Negocio

Esta guía complementa la skill `audit-me` proveyendo un marco de trabajo quirúrgico para examinar código fuente, modelos de dominio, servicios de aplicación y APIs cuando el objetivo es auditar la fidelidad y robustez de la **lógica de negocio**.

---

## 1. Los 8 Pecados Capitales de la Lógica de Negocio en Código

Al auditar código, busca activamente estos 8 patrones de degradación:

### 1. Modelo de Dominio Anémico y Lógica Dispersa (*Anemic Domain Model*)
- **Síntoma:** Clases o entidades que son meros contenedores de propiedades (`getters/setters` pasivos), mientras que las reglas reales (validaciones de negocio, cálculos de tarifas, transiciones de estado) están desparramadas en controladores, manejadores de ruta, scripts auxiliares o vistas.
- **Riesgo:** Inconsistencia total. Si una regla cambia (ej. umbral de atraso a 30 min), se debe actualizar en 5 lugares distintos; uno siempre se olvida.
- **Prueba del Auditor:** ¿Es posible instanciar o modificar la entidad dejándola en un estado que contradice las reglas de negocio sin que la propia clase lance un error? Si la respuesta es sí, el modelo es anémico.

### 2. Obsesión por Tipos Primitivos (*Primitive Obsession*)
- **Síntoma:** Usar `string`, `int` o `boolean` genéricos para conceptos densos en reglas de negocio (ej. RUT chileno, patentes vehiculares, rangos horarios, porcentajes de puntualidad, monedas con margen).
- **Riesgo:** Validaciones duplicadas y débiles. Nada impide pasar un string arbitrario como patente o un valor negativo a un odómetro.
- **Prueba del Auditor:** ¿Existen Value Objects (`Patente`, `Rut`, `VentanaHoraria`, `TarifaMargen`) que se auto-validen en su constructor y garanticen invariabilidad en todo el sistema?

### 3. Sopa de Banderas Booleanas (*Boolean Flag Soup*)
- **Síntoma:** Entidades con múltiples banderas booleanas independientes:
  `es_activo`, `es_atrasado`, `fue_reasignado`, `es_llamado_descanso`, `esta_cancelado`, `en_ruta`.
- **Riesgo:** **Explosión combinatoria y estados imposibles**. Permite aberraciones como un viaje que está `esta_cancelado = true` y simultáneamente `en_ruta = true` o `es_atrasado = true`.
- **Prueba del Auditor:** ¿El ciclo de vida del objeto está gobernado por una **Máquina de Estados Finita (FSM)** explícita con transiciones unidireccionales y guardas de negocio?

### 4. Fuga de Dominio a la Base de Datos o a la UI (*Domain Leakage*)
- **Síntoma:** Confiar en que "la base de datos se encargará" mediante constraints crudos o triggers, o peor, validar las reglas de negocio únicamente en el formulario frontend con JavaScript.
- **Riesgo:** Al consumir la lógica vía API, jobs de fondo o migraciones, las reglas se eluden por completo, corrompiendo los datos del negocio.
- **Prueba del Auditor:** Si desconectamos la base de datos y la UI, ¿el módulo de negocio sigue siendo capaz de validar y ejecutar sus reglas en memoria mediante pruebas unitarias puras?

### 5. Mutabilidad de Líneas Base y Destrucción de Evidencia
- **Síntoma:** Al ocurrir una contingencia (ej. un camión falla en andén y se cambia por otro), el código sobrescribe el registro original:
  `servicio.hora_salida_programada = nueva_hora`.
- **Riesgo:** **Distorsión fraudulenta o accidental de KPIs**. El cliente o la dirección verán que el camión salió "a la hora", ocultando el atraso real de 2 horas provocado por el proveedor de flota.
- **Prueba del Auditor:** ¿Existe inmutabilidad estricta en las líneas base planificadas? ¿Las reasignaciones quedan registradas como eventos explícitos con causa e imputabilidad?

### 6. Silenciamiento de Excepciones y Falsos Positivos (*Error Masking*)
- **Síntoma:** Bloques `try/catch` que capturan cualquier error de negocio y retornan un valor por defecto o un objeto vacío para "no romper la pantalla":
  `catch (e) { return null; }` o `catch (e) { status = 200; }`.
- **Riesgo:** Operaciones fallidas pasan desapercibidas para supervisores. Un camión puede salir a ruta con la licencia del conductor vencida porque el validador de pases capturó un timeout de red y devolvió `true` por defecto.
- **Prueba del Auditor:** ¿Los errores de negocio son tipos explícitos (`ConductorNoAcreditadoException`, `ConflictoHorarioException`) que obligan al consumidor a tomar una decisión operativa consciente?

### 7. Ambigüedad en Límites Transaccionales (*Transaction Boundary Failure*)
- **Síntoma:** Modificar recursos compartidos en pasos desacoplados sin una unidad de trabajo atómica: primero se descuenta el stock de ropa limpia, luego se marca el camión como despachado; si el segundo paso falla, el inventario queda huérfano.
- **Riesgo:** Desincronización entre el mundo físico y el digital. El sistema cree que la carga está en tránsito cuando nunca salió del andén.
- **Prueba del Auditor:** ¿La frontera de consistencia (Aggregate Root) abarca todas las entidades que deben cambiar juntas en una sola transacción ACID?

### 8. Desacoplamiento de Incentivos Humanos (*The Honest Actor Fallacy*)
- **Síntoma:** El código asume que el usuario ingresará datos fidedignos sin validación cruzada (ej. un conductor marca en la app "Llegué a faena a las 08:00" y el sistema le cree ciegamente).
- **Riesgo:** Manipulación de métricas de puntualidad y cobro indebido de bonos o tarifas.
- **Prueba del Auditor:** ¿Existe contrastación objetiva e independiente (ej. cruce de geocerca GPS satelital o confirmación por el andén receptor) frente al reporte manual?

---

## 2. Checklist Quirúrgico para el Auditor de Código

Al examinar un archivo de código fuente, aplica este cuestionario implacable:

| Área de Inspección | Pregunta Clave de Auditoría | Señal de Alarma (Red Flag) |
| :--- | :--- | :--- |
| **Definición de Entidad** | ¿La entidad protege sus invariantes en cada mutación? | Modificación directa de atributos públicos sin pasar por métodos de intención (`servicio.chofer = nuevo`). |
| **Máquina de Estados** | ¿Se validan formalmente las precondiciones de transición? | Cambiar el estado a `'Cerrado'` sin validar si pasó por `'En Ruta'` y `'En Faena'`. |
| **Cálculo de Margen/Costos** | ¿Se computan todas las variables de costo operativo en el evento? | Llamar a un conductor en descanso sin gatillar el devengo de `horas_extra` ni alterar el costo del flete. |
| **Sincronización Externa** | ¿Qué sucede si la API externa (GPS, ERP) no responde o responde basura? | Bloqueo síncrono del hilo principal o aceptación ciega de coordenadas nulas. |
| **Idempotencia** | Si el usuario presiona dos veces el botón de "Despachar", ¿qué ocurre? | Creación de dos servicios duplicados o doble asignación del mismo vehículo en el mismo horario. |

---

## 3. Ejemplo Práctico de Auditoría Crítica: Caso `ServicioLogistico`

### ❌ Código Frágil Detectado por la Auditoría:
```typescript
// MAL: Modelo anémico, lógica desparramada, sin invariantes ni idempotencia
class Servicio {
  public id: string;
  public horaProgramada: Date;
  public horaSalida: Date;
  public esAtrasado: boolean;
  public vehiculoId: string;
  public conductorId: string;
  public estado: string;

  public despachar(hora: Date) {
    this.horaSalida = hora;
    this.estado = "EN_RUTA";
    // Falla: Sobrescribe si ya estaba despachado, no valida acreditación,
    // calcula atraso con lógica débil
    if (this.horaSalida > this.horaProgramada) {
      this.esAtrasado = true;
    }
  }
}
```

### 🔴 Hallazgos de la Auditoría `audit-me`:
1. **Invariante Roto (Umbral de Negocio):** El negocio estipula que un atraso ocurre a partir de los **30 minutos**, no con 1 segundo de diferencia. Este código genera un falso positivo en el KPI de puntualidad.
2. **Puerta Abierta a Estados Inválidos:** No hay validación de si el conductor cuenta con acreditación minera ni si el vehículo tiene SOAP vigente.
3. **Ausencia de Máquina de Estados:** Se puede ejecutar `despachar()` sobre un servicio `'CANCELADO'` o `'CERRADO'` sin ninguna resistencia.
4. **Pérdida de Causa:** Si hay atraso, no se exige registrar la causa ni la imputabilidad (proveedor vs planta).

### 🟢 Solución Robusta Remediada:
```typescript
// BIEN: Entidad con invariantes de dominio, Value Objects y protección de reglas
class Servicio {
  private _estado: EstadoServicio = EstadoServicio.PROGRAMADO;
  private readonly _horaProgramada: Timestamp;
  private _horaRealSalida?: Timestamp;
  private _asignacion: AsignacionRecursos; // Vehículo + Conductor validados
  private _incidencias: Incidencia[] = [];

  constructor(id: ServicioId, horaProgramada: Timestamp, asignacion: AsignacionRecursos) {
    this.validarAcreditaciones(asignacion);
    this._horaProgramada = horaProgramada;
    this._asignacion = asignacion;
  }

  public registrarSalida(horaSalida: Timestamp, validadorGPS: GeocercaSalida): void {
    if (this._estado !== EstadoServicio.EN_ANDEN) {
      throw new TransicionEstadoInvalidaException(this._estado, EstadoServicio.EN_RUTA);
    }
    
    validadorGPS.confirmarCrucePlanta(horaSalida);
    this._horaRealSalida = horaSalida;
    this._estado = EstadoServicio.EN_RUTA;

    const desfaseMinutos = horaSalida.diferenciaEnMinutos(this._horaProgramada);
    if (desfaseMinutos > 30) {
      this.exigirRegistroIncidenciaAtraso(desfaseMinutos);
    }
  }
}
```
